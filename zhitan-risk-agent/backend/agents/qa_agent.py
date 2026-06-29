from __future__ import annotations

from schemas.risk import InterviewQuestion, TopSignal

GENERAL_QUESTIONS = [
    ("verify", "当前岗位所在团队有多少人？岗位 HC 是新增还是替补？", "团队规模"),
    ("probe", "这个岗位最近一年是否有较高流动，主要原因是什么？", "组织稳定性"),
    ("decision", "试用期转正标准、绩效占比和发薪规则分别是什么？", "薪资与转正"),
]

QUESTION_BANK = {
    "规模": [("verify", "我看到公开规模信息和招聘页展示可能存在差异，请问目前团队实际人数是多少？")],
    "劳动": [("probe", "团队在加班、绩效、调休和离职交接上有哪些明确制度？")],
    "行政": [("verify", "公司当前业务资质和合规流程是否已经完善？")],
    "融资": [("verify", "方便介绍一下最近一轮融资主体、投资方和资金规划吗？")],
    "岗位长期": [("verify", "这个岗位是新增 HC 还是替补？连续招聘较久的原因是什么？")],
    "薪资": [("decision", "薪资结构中固定、绩效、奖金和试用期比例分别是多少？")],
    "官网": [("probe", "目前核心产品、客户来源和收入模式可以具体介绍一下吗？")],
    "组织": [("probe", "岗位所在业务线近期是否有调整，团队目标是否稳定？")],
}


def generate_questions(top_signals: list[TopSignal]) -> list[InterviewQuestion]:
    questions: list[InterviewQuestion] = []
    for signal in top_signals:
        matched = False
        for key, items in QUESTION_BANK.items():
            if key in signal.signal or key in signal.explanation:
                for question_type, question in items:
                    questions.append(InterviewQuestion(id=f"q{len(questions) + 1}", type=question_type, question=question, relatedSignal=signal.signal))
                    matched = True
                    break
            if matched:
                break
    for question_type, question, related in GENERAL_QUESTIONS:
        if len(questions) >= 5:
            break
        questions.append(InterviewQuestion(id=f"q{len(questions) + 1}", type=question_type, question=question, relatedSignal=related))
    return questions[:5]
