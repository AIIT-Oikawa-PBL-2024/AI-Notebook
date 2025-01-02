"use client";

import {
	Card,
	CardBody,
	CardHeader,
	Typography,
} from "@material-tailwind/react";

export function BackgroundCard() {
	return (
		<Card
			shadow={false}
			className="relative grid h-[40rem] w-full max-w-[28rem] items-end justify-center overflow-hidden text-center"
		>
			<CardHeader
				floated={false}
				shadow={false}
				color="transparent"
				className="absolute inset-0 m-0 h-full w-full rounded-none bg-[url('/ai-notebook2.jpg')] bg-cover bg-center"
			>
				<div className="to-bg-black-10 absolute inset-0 h-full w-full bg-gradient-to-t from-black/50 via-black/30" />
			</CardHeader>
			<CardBody className="relative py-14 px-6 md:px-12">
				<Typography
					variant="h2"
					color="white"
					className="mb-6 font-medium leading-[1.5]"
				>
					AI Notebook
				</Typography>
				<Typography variant="h5" className="mb-4 text-gray-400">
					OikawaPBL 2024
				</Typography>
			</CardBody>
		</Card>
	);
}
