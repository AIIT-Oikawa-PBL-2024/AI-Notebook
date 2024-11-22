"use client";

import { GetMultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions";
import { withAuth } from "@/utils/withAuth";

type Props = {
	params: { id: string };
};

const GetMultipleChoiceQuestionsPage = ({ params }: Props) => {
	return <GetMultipleChoiceQuestions exerciseId={params.id} />;
};

export default withAuth(GetMultipleChoiceQuestionsPage as React.ComponentType);
