from sqlalchemy.orm import Session
from app.models.invoice_portal import InvoiceDocument
from app.models.finance_system import FinanceInvoiceRecord
from app.core.logging import logger

SAMPLE_INVOICES = [
    # Acme Corp
    {
        "invoice_number": "INV-1001",
        "company": "Acme Corp",
        "issue_date": "2026-01-10",
        "due_date": "2026-02-10",
        "amount": 15000.0,
        "currency": "USD",
        "status": "PAID",
        "raw_content": """============================================================
INVOICE: INV-1001
VENDOR: Acme Corp | Enterprise Cloud & Hardware Division
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-01-10
PAYMENT DUE DATE: 2026-02-10
------------------------------------------------------------
ITEMS:
1. Enterprise Cloud Subscription (Q1) - $10,000.00
2. Server Hardware Maintenance Pack - $5,000.00
------------------------------------------------------------
SUBTOTAL: $15,000.00
TAX (0%): $0.00
TOTAL DUE: $15,000.00
STATUS: PAID
============================================================"""
    },
    {
        "invoice_number": "INV-1002",
        "company": "Acme Corp",
        "issue_date": "2026-05-14",
        "due_date": "2026-06-14",
        "amount": 27500.0,
        "currency": "USD",
        "status": "PAID",
        "raw_content": """============================================================
INVOICE: INV-1002
VENDOR: Acme Corp | Enterprise Cloud & Hardware Division
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-05-14
PAYMENT DUE DATE: 2026-06-14
------------------------------------------------------------
ITEMS:
1. Enterprise Cloud Scale-Up License - $20,000.00
2. Premium 24/7 SLA Support Tier - $7,500.00
------------------------------------------------------------
SUBTOTAL: $27,500.00
TAX (0%): $0.00
TOTAL DUE: $27,500.00
STATUS: PAID
============================================================"""
    },
    {
        "invoice_number": "INV-1003",
        "company": "Acme Corp",
        "issue_date": "2026-09-20",
        "due_date": "2026-10-15",
        "amount": 48000.0,
        "currency": "USD",
        "status": "ISSUED",
        "raw_content": """============================================================
INVOICE: INV-1003
VENDOR: Acme Corp | Enterprise Cloud & Hardware Division
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-09-20
PAYMENT DUE DATE: 2026-10-15
------------------------------------------------------------
ITEMS:
1. Autonomous Agent Computing Nodes (16x H100 Cluster) - $38,000.00
2. Dedicated Bandwidth & Low-Latency Interconnect - $10,000.00
------------------------------------------------------------
SUBTOTAL: $48,000.00
TAX (0%): $0.00
TOTAL DUE: $48,000.00
STATUS: ISSUED (AWAITING FINANCE ENTRY)
============================================================"""
    },
    # Globex Corporation
    {
        "invoice_number": "INV-2001",
        "company": "Globex",
        "issue_date": "2026-03-01",
        "due_date": "2026-03-31",
        "amount": 12000.0,
        "currency": "USD",
        "status": "PAID",
        "raw_content": """============================================================
INVOICE: INV-2001
VENDOR: Globex Corporation
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-03-01
PAYMENT DUE DATE: 2026-03-31
------------------------------------------------------------
ITEMS:
1. Security & Compliance Consulting (40 hrs) - $12,000.00
------------------------------------------------------------
TOTAL DUE: $12,000.00
============================================================"""
    },
    {
        "invoice_number": "INV-2002",
        "company": "Globex",
        "issue_date": "2026-08-15",
        "due_date": "2026-09-15",
        "amount": 64000.0,
        "currency": "USD",
        "status": "ISSUED",
        "raw_content": """============================================================
INVOICE: INV-2002
VENDOR: Globex Corporation
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-08-15
PAYMENT DUE DATE: 2026-09-15
------------------------------------------------------------
ITEMS:
1. Global Network Infrastructure Upgrade - $64,000.00
------------------------------------------------------------
TOTAL DUE: $64,000.00
STATUS: ISSUED
============================================================"""
    },
    # Initech
    {
        "invoice_number": "INV-3001",
        "company": "Initech",
        "issue_date": "2026-02-18",
        "due_date": "2026-03-20",
        "amount": 9500.0,
        "currency": "USD",
        "status": "PAID",
        "raw_content": """============================================================
INVOICE: INV-3001
VENDOR: Initech Software Systems
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-02-18
PAYMENT DUE DATE: 2026-03-20
------------------------------------------------------------
ITEMS:
1. TPS Reporting Automation Plugin - $9,500.00
------------------------------------------------------------
TOTAL DUE: $9,500.00
============================================================"""
    },
    {
        "invoice_number": "INV-3002",
        "company": "Initech",
        "issue_date": "2026-07-22",
        "due_date": "2026-08-30",
        "amount": 31200.0,
        "currency": "USD",
        "status": "ISSUED",
        "raw_content": """============================================================
INVOICE: INV-3002
VENDOR: Initech Software Systems
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-07-22
PAYMENT DUE DATE: 2026-08-30
------------------------------------------------------------
ITEMS:
1. Enterprise Workflow Orchestration Suite - $31,200.00
------------------------------------------------------------
TOTAL DUE: $31,200.00
STATUS: ISSUED
============================================================"""
    },
    # Umbrella Corp
    {
        "invoice_number": "INV-4001",
        "company": "Umbrella",
        "issue_date": "2026-04-05",
        "due_date": "2026-05-05",
        "amount": 50000.0,
        "currency": "USD",
        "status": "PAID",
        "raw_content": """============================================================
INVOICE: INV-4001
VENDOR: Umbrella Pharmaceuticals & Robotics
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-04-05
PAYMENT DUE DATE: 2026-05-05
------------------------------------------------------------
ITEMS:
1. AI Research Laboratory Cleanroom Compute - $50,000.00
------------------------------------------------------------
TOTAL DUE: $50,000.00
============================================================"""
    },
    {
        "invoice_number": "INV-4002",
        "company": "Umbrella",
        "issue_date": "2026-09-01",
        "due_date": "2026-10-01",
        "amount": 89000.0,
        "currency": "USD",
        "status": "ISSUED",
        "raw_content": """============================================================
INVOICE: INV-4002
VENDOR: Umbrella Pharmaceuticals & Robotics
BILL TO: CentrAlign Internal Operations
ISSUE DATE: 2026-09-01
PAYMENT DUE DATE: 2026-10-01
------------------------------------------------------------
ITEMS:
1. Synthetic Biology Compute Cluster Allocation - $89,000.00
------------------------------------------------------------
TOTAL DUE: $89,000.00
STATUS: ISSUED
============================================================"""
    }
]

SAMPLE_FINANCE_RECORDS = [
    {
        "invoice_number": "INV-1001",
        "company": "Acme Corp",
        "amount": 15000.0,
        "due_date": "2026-02-10",
        "currency": "USD",
        "sync_status": "SYNCED",
        "notes": "Historical record processed."
    },
    {
        "invoice_number": "INV-1002",
        "company": "Acme Corp",
        "amount": 27500.0,
        "due_date": "2026-06-14",
        "currency": "USD",
        "sync_status": "SYNCED",
        "notes": "Historical record processed."
    },
    {
        "invoice_number": "INV-1003",
        "company": "Acme Corp",
        "amount": 0.0,
        "due_date": None,
        "currency": "USD",
        "sync_status": "PENDING_ENTRY",
        "notes": "Placeholder awaiting latest invoice extraction."
    },
    {
        "invoice_number": "INV-2002",
        "company": "Globex",
        "amount": 0.0,
        "due_date": None,
        "currency": "USD",
        "sync_status": "PENDING_ENTRY",
        "notes": "Placeholder for Globex latest invoice."
    },
    {
        "invoice_number": "INV-3002",
        "company": "Initech",
        "amount": 0.0,
        "due_date": None,
        "currency": "USD",
        "sync_status": "PENDING_ENTRY",
        "notes": "Placeholder for Initech latest invoice."
    },
    {
        "invoice_number": "INV-4002",
        "company": "Umbrella",
        "amount": 0.0,
        "due_date": None,
        "currency": "USD",
        "sync_status": "PENDING_ENTRY",
        "notes": "Placeholder for Umbrella latest invoice."
    }
]

def seed_initial_data(db: Session):
    logger.info("Checking and seeding database initial records...")
    
    # Check if invoice portal data exists
    if db.query(InvoiceDocument).count() == 0:
        for item in SAMPLE_INVOICES:
            db.add(InvoiceDocument(**item))
        db.commit()
        logger.info(f"Seeded {len(SAMPLE_INVOICES)} portal invoices.")
    
    # Check if finance records exist
    if db.query(FinanceInvoiceRecord).count() == 0:
        for item in SAMPLE_FINANCE_RECORDS:
            db.add(FinanceInvoiceRecord(**item))
        db.commit()
        logger.info(f"Seeded {len(SAMPLE_FINANCE_RECORDS)} finance ledger records.")

def reset_database_to_initial(db: Session):
    logger.info("Resetting database to clean initial state...")
    db.query(InvoiceDocument).delete()
    db.query(FinanceInvoiceRecord).delete()
    db.commit()
    
    for item in SAMPLE_INVOICES:
        db.add(InvoiceDocument(**item))
    for item in SAMPLE_FINANCE_RECORDS:
        db.add(FinanceInvoiceRecord(**item))
    db.commit()
    logger.info("Database reset complete.")
