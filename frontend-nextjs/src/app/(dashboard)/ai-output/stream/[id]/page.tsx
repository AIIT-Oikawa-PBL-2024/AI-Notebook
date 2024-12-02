import { GetAIOutputDisplay } from "@/features/dashboard/ai-output/stream/GetAIOutputDisplay";

type Props = {
	params: { id: string };
};

const GetAIOutputPage = ({ params }: Props) => {
	return <GetAIOutputDisplay outputId={params.id} />;
};

export default GetAIOutputPage as React.ComponentType;
