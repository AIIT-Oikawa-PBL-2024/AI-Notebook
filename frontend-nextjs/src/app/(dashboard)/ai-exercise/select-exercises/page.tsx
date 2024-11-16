"use client";

import ExerciseSelectComponent from "@/features/dashboard/ai-exercise/select-exercises/SelectExercises";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const SelectExercisesPage: NextPage = () => {
	return <ExerciseSelectComponent />;
};

export default withAuth(SelectExercisesPage as React.ComponentType);
