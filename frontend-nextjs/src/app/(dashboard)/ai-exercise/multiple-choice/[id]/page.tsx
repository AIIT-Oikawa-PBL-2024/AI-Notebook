import { GetMultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions";

type Props = {
	params: { id: string };
};

const GetMultipleChoiceQuestionsPage = ({ params }: Props) => {
	return <GetMultipleChoiceQuestions exerciseId={params.id} />;
};

export default GetMultipleChoiceQuestionsPage as React.ComponentType;
