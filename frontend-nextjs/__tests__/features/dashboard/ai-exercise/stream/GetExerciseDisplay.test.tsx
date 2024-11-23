import { GetExerciseDisplay } from "@/features/dashboard/ai-exercise/stream/GetExerciseDisplay";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { render, screen } from "@testing-library/react";
import { act } from "@testing-library/react";
import {
	type Mock,
	afterAll,
	beforeAll,
	beforeEach,
	describe,
	expect,
	it,
	vi,
} from "vitest";

vi.mock("@/providers/AuthProvider");
vi.mock("@/hooks/useAuthFetch");

// 警告を抑制
const originalConsoleError = console.error;
beforeAll(() => {
	console.error = vi.fn();
});

afterAll(() => {
	console.error = originalConsoleError;
});

describe("GetExerciseDisplay", () => {
	const mockExercise = {
		id: 1,
		title: "Test Exercise",
		response: "Test Response",
		exercise_type: "test",
		user_id: "1",
		created_at: "2024-01-01",
	};

	beforeEach(() => {
		(useAuth as Mock).mockReturnValue({ user: { uid: "test-uid" } });
		(useAuthFetch as Mock).mockReturnValue(vi.fn());
	});

	it("shows loading state initially", async () => {
		render(<GetExerciseDisplay exerciseId="1" />);
		const spinner = screen.getByRole("progressbar");
		expect(spinner).toBeInTheDocument();
	});

	it("displays error when no user is authenticated", async () => {
		(useAuth as Mock).mockReturnValue({ user: null });

		render(<GetExerciseDisplay exerciseId="1" />);

		expect(screen.getByText("認証が必要です")).toBeInTheDocument();
	});

	it("displays exercise data successfully", async () => {
		const mockFetch = vi.fn().mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockExercise),
		});
		(useAuthFetch as Mock).mockReturnValue(mockFetch);

		render(<GetExerciseDisplay exerciseId="1" />);

		await screen.findByText("AI 練習問題");
		expect(screen.getByText("Test Exercise")).toBeInTheDocument();
	});

	it("parses JSON response correctly", async () => {
		const jsonResponse = {
			content: [
				{
					input: {
						questions: [
							{ question_text: "Question 1" },
							{ question_text: "Question 2" },
						],
					},
				},
			],
		};

		const mockFetch = vi.fn().mockResolvedValue({
			ok: true,
			json: () =>
				Promise.resolve({
					...mockExercise,
					response: JSON.stringify(jsonResponse),
				}),
		});
		(useAuthFetch as Mock).mockReturnValue(mockFetch);

		render(<GetExerciseDisplay exerciseId="1" />);

		const questionText = await screen.findByText(
			(content) =>
				content.includes("Question 1") && content.includes("Question 2"),
		);
		expect(questionText).toBeInTheDocument();
	});
});
