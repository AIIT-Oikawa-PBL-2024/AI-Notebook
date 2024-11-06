"use client";

import { MultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/MultipleChoiceQuestions";
import { withAuth } from "@/utils/withAuth";

const MultipleChoiceQuestionsPage = () => {
	return <MultipleChoiceQuestions />;
};

export default withAuth(MultipleChoiceQuestionsPage as React.ComponentType);
