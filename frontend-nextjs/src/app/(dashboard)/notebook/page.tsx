"use client";

import { NotebookForm } from "@/features/dashboard/notebook/components/NotebookForm";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const NotebookPage: NextPage = () => {
	return <NotebookForm />;
};

export default withAuth(NotebookPage as React.ComponentType);
