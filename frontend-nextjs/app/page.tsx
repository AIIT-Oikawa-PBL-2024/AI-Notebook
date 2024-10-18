import FileUpload from "@/features/file/FileUpload";
import Image from "next/image";

export default function UploadPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        ファイルアップロード
      </h1>
      <div className="max-w-xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
        <div className="p-6">
          <FileUpload />
        </div>
        <div className="mt-6">
          <Image
            src="/pbl-flyer.jpg"
            alt="アプリの説明画像"
            width={500}
            height={300}
            layout="responsive"
            className="rounded-b-lg"
          />
        </div>
      </div>
    </div>
  );
}
