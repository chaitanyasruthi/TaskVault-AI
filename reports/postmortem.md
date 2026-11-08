# TaskVault AI – Postmortem Report

## 1. Project Overview

TaskVault AI executes approved programming tasks inside isolated Celesto cloud sandboxes. It uses FastAPI for the backend and PostgreSQL for execution tracking.

The system also supports persistent sandbox lifecycle management, including stopping, resuming, and deleting Celesto computers.

## 2. Issues Encountered

### Issue 1: Python Not Found

**Problem:** Fresh Celesto sandboxes did not have Python installed.

**Impact:** Python program execution failed.

**Resolution:** Implemented automatic Python detection and installation using APT before executing programs.

**Result:** Python 3.12.3 was installed successfully in fresh sandboxes.

### Issue 2: PostgreSQL Port Conflict

**Problem:** Local PostgreSQL already occupied port 5432.

**Impact:** Docker PostgreSQL could not bind to the default host port.

**Resolution:** Changed the Docker host port mapping to 5433.

**Result:** PostgreSQL container started successfully.

### Issue 3: Celesto Sandbox Rate Limiting

**Problem:** Celesto cloud sandbox creation returned an HTTP 429 rate-limit error.

**Impact:** New sandbox creation was temporarily unavailable.

**Resolution:** Avoided repeated creation attempts and waited before retrying.

**Result:** Sandbox creation subsequently succeeded.

### Issue 4: Celesto Computer ID Persistence

**Problem:** Earlier executions did not save the Celesto computer ID because the computer was not explicitly started before reading its ID.

**Impact:** Persistent sandbox reconnection could not be reliably tested.

**Resolution:** Updated the execution service to start the Celesto computer before retrieving its ID and save that ID in PostgreSQL.

**Result:** Run #46 successfully returned and stored computer ID `cmp_0924a799e4ca`.

## 3. Successful Execution Tests

| Test | Result |
|---|---|
| Hello World | Passed |
| Addition | Passed |
| Factorial | Passed |
| Persistent sandbox creation | Passed |
| Persistent sandbox stop | Passed |
| Persistent sandbox resume | Passed |
| Resume verification command | Passed |
| Persistent sandbox deletion | Passed |

Run #46 executed the Python Hello World program successfully with exit code 0.

The same persistent computer was resumed using its stored ID. The verification command returned `TASKVAULT_RESUMED`.

The computer was subsequently deleted, and the Celesto dashboard showed zero active sandboxes.

Five successful Python executions have been measured and documented. The 20-run reliability target is still pending.

## 4. Lessons Learned

- Fresh execution environments require runtime provisioning.
- Cloud sandbox creation must account for provider rate limits.
- Computer IDs must be stored to support persistent sandbox reconnection.
- Persistent computers can be stopped and resumed instead of recreated.
- Every execution should have an audit record.
- Sandbox cleanup must be attempted after success or failure.
- Reliability must be measured using repeated executions.

## 5. Remaining Work

- Complete at least 20 reliability test runs.
- Measure boot-to-ready time and execution cost.
- Complete malicious command containment testing.
- Implement and test failure recovery policies.
- Evaluate additional Celesto capabilities.
- Test concurrent execution.
- Improve security validation and prompt-injection resistance.

## 6. Conclusion

TaskVault AI has demonstrated successful Python program execution inside real Celesto cloud sandboxes.

Run #46 additionally demonstrated persistent computer ID storage, sandbox stopping, reconnection, command verification, and deletion.

The implementation has passed initial cloud validation. Further reliability, security, concurrency, and failure-recovery testing is required before the system can be considered complete.