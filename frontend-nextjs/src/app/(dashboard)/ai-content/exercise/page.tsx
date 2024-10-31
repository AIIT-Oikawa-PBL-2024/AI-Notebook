"use client";

import { ExerciseDisplay } from "@/features/(dashboard)/ai-content/exercise/ExerciseDisplay";
import { useExerciseGenerator } from "@/hooks/useExerciseGenerator";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const CreateExercisePage: NextPage = () => {
	const { loading, error, exercise } = useExerciseGenerator();

	return (
		<div className="container mx-auto p-4">
			<ExerciseDisplay loading={loading} error={error} exercise={exercise} />
		</div>
	);
};

export default withAuth(CreateExercisePage as React.ComponentType);
