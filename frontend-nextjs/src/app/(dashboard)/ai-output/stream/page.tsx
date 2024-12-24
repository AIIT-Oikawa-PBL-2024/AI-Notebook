"use client";

import { OutputDisplay } from "@/features/dashboard/ai-output/stream/OutputDisplay";
import { useOutputGenerator } from "@/features/dashboard/ai-output/stream/hooks/useOutputGenerator";
import { Button } from "@material-tailwind/react";
import type { NextPage } from "next";

const CreateOutputPage: NextPage = () => {
	const { loading, error, output, resetOutput } = useOutputGenerator();

	return (
		<div className="container mx-auto p-4">
			<OutputDisplay loading={loading} error={error} output={output} />
			{!loading && output && (
				<Button onClick={resetOutput}>新しいノートを生成</Button>
			)}
		</div>
	);
};

export default CreateOutputPage as React.ComponentType;
