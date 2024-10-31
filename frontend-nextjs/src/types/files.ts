export interface FileData {
	file_name: string;
	file_size: string;
	created_at: string;
	select?: boolean;
	id?: string;
	user_id?: string;
}

export interface DeleteResponse {
	success: boolean;
	failed_files?: string[];
	error?: string;
}
