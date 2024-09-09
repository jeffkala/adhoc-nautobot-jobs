"""Custom Compliance via Custom Field Optional Parameters."""
from netutils.config.compliance import feature_compliance
from netutils.config.clean import clean_config, sanitize_config

def custom_compliance_func(obj):
    logger.debug("Custom Compliance Function via job repo logger")
    compliance_int = 1
    compliance = True
    ordered = True
    missing = ""
    extra = ""
    return {
        "compliance": compliance,
        "compliance_int": compliance_int,
        "ordered": ordered,
        "missing": missing,
        "extra": extra,
    }
