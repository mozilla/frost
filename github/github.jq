[.report.tests[] | select(.call.outcome != "passed")
    | { full_name: .name,
        modified_status: .outcome,
        original_status: .metadata[0].outcome,
        reason:(.call.xfail_reason // ""),
        longrepr: .call.longrepr
    }
]
