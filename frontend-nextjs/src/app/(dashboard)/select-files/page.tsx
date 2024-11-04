"use client";

import FileSelectComponent from "@/features/dashboard/select-files/SelectFiles";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const SelectFilesPage: NextPage = () => {
	return <FileSelectComponent />;
};

export default withAuth(SelectFilesPage as React.ComponentType);
