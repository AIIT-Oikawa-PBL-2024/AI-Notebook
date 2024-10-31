"use client";

import CreateOutput from "@/features/(dashboard)/CreateOutput";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const AIOutputPage: NextPage = () => {
	return (
		<div className="container mx-auto px-4 py-8">
			<h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
				AIノート
			</h1>
			<div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
				<CreateOutput />
			</div>
		</div>
	);
};

export default withAuth(AIOutputPage as React.ComponentType);
