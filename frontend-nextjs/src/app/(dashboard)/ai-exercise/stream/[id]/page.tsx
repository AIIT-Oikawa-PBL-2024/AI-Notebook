"use client";

import { GetExerciseDisplay } from "@/features/dashboard/ai-exercise/stream/GetExerciseDisplay";
import { withAuth } from "@/utils/withAuth";

type Props = {
	params: { id: string };
};

const GetExercisePage = ({ params }: Props) => {
	return <GetExerciseDisplay exerciseId={params.id} />;
};

export default withAuth(GetExercisePage as React.ComponentType);
