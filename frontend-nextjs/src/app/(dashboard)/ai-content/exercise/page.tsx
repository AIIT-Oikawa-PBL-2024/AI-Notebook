"use client";

import { ExerciseDisplay } from "@/features/(dashboard)/ai-content/exercise/ExerciseDisplay";
import { useExerciseGenerator } from "@/hooks/useExerciseGenerator";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const CreateExercisePage: NextPage = () => {
	const { loading, error, exercise, resetExercise } = useExerciseGenerator();

	return (
		<div className="container mx-auto p-4">
			<ExerciseDisplay loading={loading} error={error} exercise={exercise} />
			{!loading && exercise && (
				<button
					type="button"
					onClick={resetExercise}
					className="mt-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
				>
					新しい問題を生成
				</button>
			)}
		</div>
	);
};

export default withAuth(CreateExercisePage as React.ComponentType);
