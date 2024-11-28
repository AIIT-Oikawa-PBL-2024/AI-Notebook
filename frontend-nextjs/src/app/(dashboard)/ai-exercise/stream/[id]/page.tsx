import { GetExerciseDisplay } from "@/features/dashboard/ai-exercise/stream/GetExerciseDisplay";

type Props = {
	params: { id: string };
};

const GetExercisePage = ({ params }: Props) => {
	return <GetExerciseDisplay exerciseId={params.id} />;
};

export default GetExercisePage as React.ComponentType;
