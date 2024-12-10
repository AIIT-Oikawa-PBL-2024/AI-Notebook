"use client";

import { ExerciseDisplay } from "@/features/dashboard/ai-exercise/stream/ExerciseDisplay";
import { useExerciseGenerator } from "@/features/dashboard/ai-exercise/stream/useExerciseGenerator";
import type { NextPage } from "next";

const CreateExercisePage: NextPage = () => {
	const { loading, error, exercise, title, resetExercise } =
		useExerciseGenerator();

	return (
		<div
			className="container mx-auto p-4"
			data-testid="exercise-page-container"
		>
			<ExerciseDisplay
				loading={loading}
				error={error}
				exercise={exercise}
				title={title}
			/>
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

export default CreateExercisePage as React.ComponentType;
