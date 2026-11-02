"""Generate tests/fixtures/guide_mini.csv: a small synthetic file with GUIDE's columns.

Contents (seed 42, deterministic):
- 40 labelled in-scope incidents over 3 categories and 4 organisations;
- 2 multi-category incidents (one majority case, one tie -> alphabetical first);
- 1 incident whose rows are partly unlabelled (those rows must be dropped);
- 3 fully unlabelled incidents and 4 out-of-scope incidents (must be excluded);
- 2 incidents sharing the same first timestamp (ordering tie-break by OrgId, IncidentId);
- typed entities whose identity field holds the sentinel (about 25 %);
- more entity types, Roles values and MITRE techniques than the vocabulary sizes,
  so that the ``other`` buckets are exercised.

Run: python tests/fixtures/make_guide_mini.py
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence

HEADER: Sequence[str] = (
    "Id,OrgId,IncidentId,AlertId,Timestamp,DetectorId,AlertTitle,Category,MitreTechniques,"
    "IncidentGrade,ActionGrouped,ActionGranular,EntityType,EvidenceRole,DeviceId,Sha256,"
    "IpAddress,Url,AccountSid,AccountUpn,AccountObjectId,AccountName,DeviceName,"
    "NetworkMessageId,EmailClusterId,RegistryKey,RegistryValueName,RegistryValueData,"
    "ApplicationId,ApplicationName,OAuthApplicationId,ThreatFamily,FileName,FolderPath,"
    "ResourceIdName,ResourceType,Roles,OSFamily,OSVersion,AntispamDirection,SuspicionLevel,"
    "LastVerdict,CountryCode,State,City"
).split(",")

# The most frequent value of each identity field in GUIDE means "absent" (data audit).
SENTINELS = {
    "DeviceId": "98799", "Sha256": "138268", "IpAddress": "360606", "Url": "160396",
    "AccountSid": "441377", "AccountUpn": "673934", "AccountObjectId": "425863",
    "AccountName": "453297", "DeviceName": "153085", "NetworkMessageId": "529644",
    "RegistryKey": "1631", "RegistryValueName": "635", "RegistryValueData": "860",
    "ApplicationId": "2251", "ApplicationName": "3421", "OAuthApplicationId": "881",
    "FileName": "289573", "FolderPath": "117668", "ResourceIdName": "3586",
    "OSFamily": "5", "OSVersion": "66", "CountryCode": "242", "State": "1445", "City": "10630",
}
IDENTITY_FIELD = {
    "User": "AccountObjectId", "Machine": "DeviceId", "Ip": "IpAddress", "Url": "Url",
    "File": "Sha256", "MailMessage": "NetworkMessageId", "Mailbox": "AccountUpn",
    "CloudApplication": "ApplicationId",
}
ENTITY_TYPES = [
    "Ip", "User", "MailMessage", "Machine", "File", "Url", "Mailbox", "Process",
    "CloudLogonRequest", "CloudApplication", "RegistryValue", "RegistryKey", "AzureResource",
    "MailCluster", "CloudLogonSession", "ActiveDirectoryDomain", "Blob", "OAuthApplication",
    "BlobContainer", "SecurityGroup",
]
ROLES = ["", "", "", "Contextual", "Destination", "Source", "Suspicious", "Attacker",
         "Victim", "Compromised", "PolicyViolator", "Edge"]
MITRE = ["T1" + n for n in ("566", "078", "110", "189", "204", "059", "071", "105", "133",
                            "136", "027", "036", "048", "041", "567", "114", "098", "003",
                            "087", "021", "528", "530", "539", "550", "090")]
SUSPICION = ["", "", "", "Suspicious", "Incriminated"]
VERDICT = ["", "", "Suspicious", "Malicious", "NoThreatsFound",
           "DomainPII_50d8b4a941c26b89482c94ab324b5a274f9ced66"]
CATEGORIES = ["InitialAccess", "SuspiciousActivity", "Exfiltration"]
OUT_OF_SCOPE = ["CommandAndControl", "Execution"]
GRADES = ["TruePositive", "BenignPositive", "FalsePositive"]

START = datetime(2024, 6, 1)


def _ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


class Gen:
    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.rows: list[dict[str, str]] = []
        self.next_alert = 1000
        self.next_row = 1

    def evidence(self, org: int, inc: int, alert: int, ts: datetime, category: str,
                 grade: str, mitre: str) -> None:
        rng = self.rng
        etype = rng.choice(ENTITY_TYPES)
        row = {c: "" for c in HEADER}
        row.update(SENTINELS)
        row.update({
            "Id": str(self.next_row), "OrgId": str(org), "IncidentId": str(inc),
            "AlertId": str(alert), "Timestamp": _ts(ts),
            "DetectorId": str(rng.randint(1, 50)), "AlertTitle": str(rng.randint(1, 500)),
            "Category": category, "MitreTechniques": mitre, "IncidentGrade": grade,
            "EntityType": etype, "EvidenceRole": rng.choice(["Impacted", "Related", "Related"]),
            "Roles": rng.choice(ROLES), "SuspicionLevel": rng.choice(SUSPICION),
            "LastVerdict": rng.choice(VERDICT),
            "ResourceType": rng.choice(["", "", "", "", "Virtual Machine"]),
            "ThreatFamily": rng.choice(["", "", "", "", "", "Phish"]),
        })
        field = IDENTITY_FIELD.get(etype)
        if field and rng.random() >= 0.25:
            # Small ID pool so the same entity recurs across incidents (alias reuse).
            # Otherwise the field keeps its sentinel ("absent") value.
            row[field] = str(rng.randint(1, 12))
        self.rows.append(row)
        self.next_row += 1

    def incident(self, org: int, inc: int, start: datetime, categories: list[str],
                 grade: str, n_evidence: tuple[int, int] = (1, 4),
                 unlabelled_alert: bool = False) -> None:
        for i, category in enumerate(categories):
            alert = self.next_alert
            self.next_alert += 1
            ts = start + timedelta(minutes=7 * i)
            k = self.rng.randint(1, 3)
            mitre = ";".join(sorted(self.rng.sample(MITRE, k))) if self.rng.random() < 0.7 else ""
            g = "" if unlabelled_alert and i == len(categories) - 1 else grade
            for _ in range(self.rng.randint(*n_evidence)):
                self.evidence(org, inc, alert, ts, category, g, mitre)


def generate(seed: int = 42) -> list[dict[str, str]]:
    g = Gen(seed)
    rng = g.rng
    inc = 100
    for i in range(36):
        inc += 1
        n_alerts = rng.choice([1, 1, 1, 2, 3])
        cat = CATEGORIES[i % 3]
        start = START + timedelta(hours=7 * i + rng.randint(0, 3))
        g.incident(i % 4, inc, start, [cat] * n_alerts, rng.choice(GRADES))
    # Multi-category, majority: 2 SuspiciousActivity alerts vs 1 InitialAccess.
    g.incident(1, 201, START + timedelta(hours=60),
               ["InitialAccess", "SuspiciousActivity", "SuspiciousActivity"], "TruePositive")
    # Multi-category tie: 1 InitialAccess vs 1 Exfiltration -> Exfiltration (alphabetical).
    g.incident(2, 202, START + timedelta(hours=120), ["InitialAccess", "Exfiltration"],
               "BenignPositive")
    # Same first timestamp as each other: order by OrgId then IncidentId.
    tie = START + timedelta(hours=200)
    g.incident(3, 203, tie, ["InitialAccess"], "FalsePositive")
    # Partly unlabelled: its last alert has an empty IncidentGrade.
    g.incident(0, 204, tie, ["Exfiltration", "Exfiltration"], "FalsePositive",
               unlabelled_alert=True)
    # Fully unlabelled (excluded).
    for j, h in enumerate((30, 90, 150)):
        g.incident(j, 301 + j, START + timedelta(hours=h), [CATEGORIES[j]], "")
    # Out of scope (excluded).
    for j, h in enumerate((10, 70, 130, 190)):
        g.incident(j, 401 + j, START + timedelta(hours=h), [OUT_OF_SCOPE[j % 2]],
                   rng.choice(GRADES))
    rows = g.rows
    rng.shuffle(rows)  # raw files are not ordered by incident
    return rows


def main() -> None:
    out = Path(__file__).with_name("guide_mini.csv")
    rows = generate()
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
