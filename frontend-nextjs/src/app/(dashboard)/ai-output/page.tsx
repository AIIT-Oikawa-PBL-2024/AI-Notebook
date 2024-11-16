"use client";

import { OutputDisplay } from "@/features/dashboard/ai-output/OutputDisplay";
import { useOutputGenerator } from "@/features/dashboard/ai-output/hooks/useOutputGenerator";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const CreateOutputPage: NextPage = () => {
	const { loading, error, output, resetOutput } = useOutputGenerator();

	return (
		<div className="container mx-auto p-4">
			<OutputDisplay loading={loading} error={error} output={output} />
			{!loading && output && (
				<button
					type="button"
					onClick={resetOutput}
					className="mt-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
				>
					新しいノートを生成
				</button>
			)}
		</div>
	);
};

export default withAuth(CreateOutputPage as React.ComponentType);