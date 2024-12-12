import { GetEssayQuestions } from "@/features/dashboard/ai-exercise/essay-question/GetEssayQuestions";

type Props = {
	params: { id: string };
};

const GetEssayQuestionsPage = ({ params }: Props) => {
	return <GetEssayQuestions exerciseId={params.id} />;
};

export default GetEssayQuestionsPage as React.ComponentType;
