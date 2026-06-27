import sys
from pathlib import Path
sys.path.append(str(Path('src').absolute()))
from flozai.core.intent_parser import IntentParser
from flozai.core.workflow_builder import WorkflowBuilder
from flozai.core.validator import WorkflowValidator
p = IntentParser()
i = p.parse('Use AI to generate a motivational quote, then send it to a webhook')
wb = WorkflowBuilder()
wf = wb.build(i)
v = WorkflowValidator()
valid, errs = v.validate(wf)
print(f'Valid: {valid}, Errors: {errs}')
