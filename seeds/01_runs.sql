INSERT INTO agent_runs (
    sandbox_name,
    task,
    status,
    execution_target,
    result
)
VALUES (
    'sbx-seeddemo1',
    'TaskVault AI demonstration seed run',
    'completed',
    'celesto_sandbox',
    '{"message": "Seed demonstration record", "execution_target": "celesto_sandbox"}'::json
)
ON CONFLICT (sandbox_name) DO NOTHING;
