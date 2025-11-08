# User Validation Plan - AEO Box v1.5

**Purpose**: Ensure each sprint delivers real user value through structured validation testing
**Timeline**: Sprint 2, 3, and 4 completion
**Method**: Usability testing with representative users

---

## Overview

This validation plan ensures that the v1.5 Multi-Agent System meets user needs at each sprint milestone. We conduct three validation checkpoints:

1. **Sprint 2 Checkpoint** (Day 8): Beta user testing of agent functionality
2. **Sprint 3 Checkpoint** (Day 11.5): Workflow usability testing
3. **Sprint 4 Checkpoint** (Day 16): New user onboarding testing

---

## Sprint 2: Beta User Testing (5 Users)

### Timing
**When**: End of Day 8 (after all 6 agents implemented)
**Duration**: 2-3 hours per user session
**Total Effort**: 10-15 hours

### Objectives
- Validate that agents produce useful, actionable outputs
- Baseline agent processing time (supports "2-3 hours → 2 min" claim)
- Identify critical usability issues before workflows built

### Participant Criteria
**Who to recruit**:
- 3 SEO specialists (primary user persona)
- 1 content marketer
- 1 agency owner

**Requirements**:
- Experience with content optimization
- Familiar with SEO/AEO concepts
- Available for 2-hour testing session

### Test Scenarios

#### Scenario 1: Content Auditor Agent (30 min)
**Task**: "Run the Content Auditor agent on this sample article and review the output."

**Sample Input**:
```python
from agentic_aeo import get_campaign_store, OrchestratorAgent, AuditorAgent

orchestrator = OrchestratorAgent()
auditor = AuditorAgent()
orchestrator.register_agent(AgentType.AUDITOR, auditor)

result = await auditor.execute_task(TaskMessage(
    task_id="test_audit",
    task_type=TaskType.AUDIT_CONTENT,
    agent_type=AgentType.AUDITOR,
    campaign_id="test",
    input_data={"url": "https://example.com/article", "content": "..."},
))

print(result.output_data)
```

**Success Criteria**:
- [ ] User understands the E-E-A-T scores
- [ ] Recommendations are actionable
- [ ] Output completes in <2 minutes
- [ ] User would use this in their workflow

**Questions to Ask**:
1. "Is the E-E-A-T analysis helpful? What's missing?"
2. "Are the improvement recommendations clear and actionable?"
3. "How long would this analysis take you manually?" (baseline)
4. "Would you use this tool for your content audits?"

---

#### Scenario 2: Content Optimizer Agent (30 min)
**Task**: "Run the Content Optimizer on the audited article. Review the suggested improvements."

**Success Criteria**:
- [ ] Optimizations preserve brand voice
- [ ] Before/after diff is clear
- [ ] User can accept/reject changes
- [ ] Processing completes in <2 minutes

**Questions to Ask**:
1. "Do the optimizations improve the content?"
2. "Does it maintain the original tone and brand voice?"
3. "How long would these edits take you manually?" (baseline)
4. "What improvements would you make to this feature?"

---

#### Scenario 3: Citation Tracker Agent (30 min)
**Task**: "Track citations for these 3 queries using the Citation Tracker."

**Success Criteria**:
- [ ] Citation results are accurate
- [ ] Multi-LLM tracking works (Claude, ChatGPT, etc.)
- [ ] CSV export is useful
- [ ] Processing completes in <5 minutes

**Questions to Ask**:
1. "Are the citation results accurate?"
2. "Is tracking across multiple LLMs valuable to you?"
3. "Would you use this data to inform content strategy?"

---

### Data Collection

**Quantitative Metrics**:
- Agent processing time (seconds) for each scenario
- Task completion rate (% of users who complete each scenario)
- Error rate (number of errors encountered)

**Qualitative Feedback**:
- Usefulness rating (1-5 scale): "How useful is this agent's output?"
- Ease of use rating (1-5 scale): "How easy was it to use this agent?"
- Likelihood to use (1-5 scale): "How likely are you to use this in your workflow?"
- Open feedback: "What would improve this agent?"

**Validation Criteria**:
- ✅ **PASS**: Average usefulness ≥4.0, processing time <5 min, 80%+ would use
- ⚠️ **NEEDS IMPROVEMENT**: Average usefulness 3.0-3.9, some users would use
- ❌ **FAIL**: Average usefulness <3.0, majority would not use

---

## Sprint 3: Workflow Usability Testing (9 Users)

### Timing
**When**: End of Day 11.5 (after CLI + API + workflows complete)
**Duration**: 1.5-2 hours per user session
**Total Effort**: 13-18 hours

### Objectives
- Validate `/aeo-campaign` workflow is intuitive and useful
- Test CLI commands for ease of use
- Verify API integration is straightforward
- Baseline complete workflow time (supports "<5 min" claim)

### Participant Criteria
**Who to recruit**:
- 5 SEO specialists (primary users)
- 2 developers (API integration users)
- 2 agency owners (CLI users)

**Requirements**:
- Comfortable with command line (for CLI testing)
- Familiar with REST APIs (for API testing)
- Available for 90-minute session

### Test Scenarios

#### Scenario 1: CLI - Complete Campaign Workflow (45 min)
**Task**: "Run a complete AEO campaign on this sample URL using the CLI."

**Commands to Test**:
```bash
# Install and setup
pip install -e agentic-aeo
aeo --help

# Run campaign
aeo campaign --url "https://example.com/article" \
  --queries "query1,query2,query3" \
  --mode comprehensive

# Check status
aeo status --campaign-id camp_123

# View report
cat .aeo-agent-data/campaigns/camp_123/outputs/report.md
```

**Success Criteria**:
- [ ] Installation is straightforward
- [ ] `--help` output is clear and helpful
- [ ] Campaign completes without errors
- [ ] Report is useful and actionable
- [ ] Total workflow time <5 minutes

**Questions to Ask**:
1. "Was the installation process clear?"
2. "Did the `--help` text guide you effectively?"
3. "Were error messages (if any) helpful?"
4. "How long would this workflow take manually?" (baseline)
5. "What would make the CLI easier to use?"

---

#### Scenario 2: API - Campaign Integration (30 min)
**Task**: "Integrate the AEO campaign into this sample application using the REST API."

**API Calls to Test**:
```python
import requests

# Create campaign
response = requests.post("http://localhost:8000/api/v1/campaigns", json={
    "url": "https://example.com/article",
    "queries": ["query1", "query2"],
    "mode": "comprehensive"
})
campaign_id = response.json()["campaign_id"]

# Poll for status
while True:
    status = requests.get(f"http://localhost:8000/api/v1/campaigns/{campaign_id}")
    if status.json()["status"] == "completed":
        break

# Get results
results = status.json()["results"]
```

**Success Criteria**:
- [ ] API documentation is clear (Swagger UI)
- [ ] Authentication works (if implemented)
- [ ] Response format is intuitive
- [ ] Error messages are helpful
- [ ] Integration takes <30 minutes

**Questions to Ask**:
1. "Was the API documentation clear and complete?"
2. "Were request/response formats intuitive?"
3. "Did error messages help you debug issues?"
4. "Would you integrate this into your application?"

---

#### Scenario 3: Competitive Analysis Workflow (15 min)
**Task**: "Run a competitive analysis comparing 3 competitor URLs."

**Commands**:
```bash
aeo compete \
  --urls "url1,url2,url3" \
  --query "target query" \
  --output comparison-report.md
```

**Success Criteria**:
- [ ] Command is intuitive
- [ ] Comparison report is useful
- [ ] Processing completes in reasonable time
- [ ] Insights are actionable

---

### Data Collection

**Quantitative Metrics**:
- Workflow completion time (minutes)
- Task success rate (% completing without assistance)
- Error frequency (number of errors per session)
- Time-to-first-success (minutes from install to first working workflow)

**Qualitative Feedback**:
- Intuitiveness rating (1-5): "How intuitive were the workflows?"
- Error message quality (1-5): "How helpful were error messages?"
- Documentation quality (1-5): "How helpful was the documentation?"
- Likelihood to use (1-5): "How likely are you to use this tool?"

**Validation Criteria**:
- ✅ **PASS**: Average intuitiveness ≥4.0, workflow time <5 min, 80%+ completion rate
- ⚠️ **NEEDS IMPROVEMENT**: Average 3.0-3.9, some usability issues
- ❌ **FAIL**: Average <3.0, majority struggle to complete workflows

---

## Sprint 4: New User Onboarding Testing

### Timing
**When**: Day 16 (after all documentation complete)
**Duration**: 1 hour per user session
**Total Effort**: 6-8 hours

### Objectives
- Validate quick start guide is clear and complete
- Test first-run experience (if implemented)
- Measure time-to-first-successful-workflow
- Identify documentation gaps

### Participant Criteria
**Who to recruit**:
- 6 users who have NEVER used AEO Box before
- Mix of SEO specialists and developers
- Available for 1-hour remote session

**Requirements**:
- No prior knowledge of AEO Box
- Comfortable with Python and CLI
- Available immediately (no advance preparation)

### Test Scenarios

#### Scenario 1: First-Time Installation (20 min)
**Task**: "Install AEO Box and run your first campaign using only the README."

**Instructions** (give to user):
> "You've just discovered AEO Box on GitHub. Your goal is to install it and run your first AEO campaign on this sample article. Use only the README.md and documentation - don't ask me for help unless you're completely stuck."

**Success Criteria**:
- [ ] User installs without assistance
- [ ] User completes first campaign without assistance
- [ ] Total time <20 minutes
- [ ] User understands what happened

**Observation Points**:
- Where do they get stuck?
- What documentation do they reference?
- Do they find the quick start guide?
- Do they understand configuration (.env setup)?

---

#### Scenario 2: API Integration (20 min)
**Task**: "Integrate AEO Box into your application using the API documentation."

**Success Criteria**:
- [ ] User finds API documentation (Swagger UI)
- [ ] User makes first successful API call
- [ ] User understands authentication (if required)
- [ ] Total time <20 minutes

---

#### Scenario 3: Troubleshooting (20 min)
**Task**: "Your campaign failed with an error. Use the documentation to debug and fix it."

**Inject Error**: Provide invalid API key or malformed input

**Success Criteria**:
- [ ] User finds error in logs
- [ ] User references troubleshooting guide
- [ ] User resolves issue without assistance
- [ ] Error message was helpful

---

### Data Collection

**Quantitative Metrics**:
- Time-to-install (minutes)
- Time-to-first-workflow (minutes from install to successful campaign)
- Documentation lookup frequency (times user referenced docs)
- Assistance requests (times user needed help)

**Qualitative Feedback**:
- README clarity (1-5): "How clear was the README?"
- Quick start usefulness (1-5): "Did the quick start guide help?"
- Error message quality (1-5): "Were error messages helpful?"
- Overall onboarding (1-5): "How smooth was the onboarding experience?"

**Validation Criteria**:
- ✅ **PASS**: Time-to-first-workflow <20 min, average onboarding ≥4.0, <2 assistance requests
- ⚠️ **NEEDS IMPROVEMENT**: Time 20-30 min, average 3.0-3.9
- ❌ **FAIL**: Time >30 min, average <3.0, frequent assistance needed

---

## Success Metrics Summary

### Sprint 2 Targets
- [ ] Agent processing time: <5 minutes average
- [ ] Usefulness rating: ≥4.0/5.0
- [ ] Likelihood to use: ≥80%
- [ ] Manual time baseline: 2-3 hours → <5 min (measured)

### Sprint 3 Targets
- [ ] Workflow completion time: <5 minutes average
- [ ] Intuitiveness rating: ≥4.0/5.0
- [ ] Task completion rate: ≥80%
- [ ] API integration time: <30 minutes

### Sprint 4 Targets
- [ ] Time-to-first-workflow: <20 minutes
- [ ] Onboarding rating: ≥4.0/5.0
- [ ] Assistance requests: <2 per user
- [ ] Documentation clarity: ≥4.0/5.0

---

## Reporting

After each validation checkpoint, create a summary report:

### Template

```markdown
# User Validation Report - Sprint X

**Date**: YYYY-MM-DD
**Sprint**: X
**Participants**: N users
**Session Duration**: X hours total

## Quantitative Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Processing time | <5 min | X.X min | ✅/❌ |
| Usefulness rating | ≥4.0 | X.X/5.0 | ✅/❌ |
| Completion rate | ≥80% | XX% | ✅/❌ |

## Qualitative Feedback

**Strengths**:
- Positive feedback point 1
- Positive feedback point 2

**Issues Identified**:
1. Critical issue (blocks usage)
2. Important issue (degrades experience)
3. Minor issue (polish)

## Recommendations

**Must Fix** (before v1.5 release):
- [ ] Issue 1
- [ ] Issue 2

**Should Fix** (v1.6 backlog):
- [ ] Enhancement 1
- [ ] Enhancement 2

## Conclusion

Overall validation: ✅ PASS / ⚠️ NEEDS IMPROVEMENT / ❌ FAIL
```

---

## Budget & Resources

### User Recruitment
- **Sprint 2**: 5 users × $100 incentive = $500
- **Sprint 3**: 9 users × $100 incentive = $900
- **Sprint 4**: 6 users × $75 incentive = $450
- **Total Budget**: $1,850

### Time Investment
- **Sprint 2**: 10-15 hours (testing + analysis)
- **Sprint 3**: 13-18 hours (testing + analysis)
- **Sprint 4**: 6-8 hours (testing + analysis)
- **Total Time**: 29-41 hours

### Tools
- **Video conferencing**: Zoom (screen sharing + recording)
- **Survey tool**: Google Forms (free)
- **Analytics**: Spreadsheet for quantitative data

---

## Next Steps

1. **Before Sprint 2**: Recruit 5 beta users
2. **Day 8**: Conduct Sprint 2 validation
3. **Day 9**: Analyze results and create action items
4. **Before Sprint 3**: Recruit 9 workflow testers
5. **Day 11.5**: Conduct Sprint 3 validation
6. **Day 12**: Analyze results and prioritize fixes
7. **Before Sprint 4**: Recruit 6 new users
8. **Day 16**: Conduct Sprint 4 validation
9. **Post-v1.5**: Create final validation summary

---

**Document Owner**: Product Owner
**Last Updated**: 2025-01-08
**Status**: Ready for execution
