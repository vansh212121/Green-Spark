import React, { useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { useRequestUploadUrlMutation, useConfirmBillUploadMutation } from '@/features/api/billApi';

export const BillUploadZone = () => {
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef(null);

    const [requestUploadUrl] = useRequestUploadUrlMutation();
    const [confirmBillUpload] = useConfirmBillUploadMutation();

    const handleFileSelect = (event) => {
        const file = event.target.files?.[0];
        if (file) {
            handleUpload(file);
        }
        // Reset the file input to allow uploading the same file again
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleUpload = async (file) => {
        setIsUploading(true);

        const uploadPromise = async () => {
            // Step 1: Request a presigned URL from our backend
            const uploadConfig = await requestUploadUrl({
                filename: file.name,
                content_type: file.type,
            }).unwrap();

            // Step 2: Upload the file directly to MinIO/S3 using the presigned URL
            const s3Response = await fetch(uploadConfig.upload_url, {
                method: 'PUT',
                body: file,
                headers: {
                    'Content-Type': file.type,
                },
            });

            if (!s3Response.ok) {
                throw new Error('File upload to storage failed.');
            }

            // Step 3: Confirm the upload with our backend to trigger parsing
            await confirmBillUpload({ file_uri: uploadConfig.file_uri }).unwrap();
        };

        toast.promise(uploadPromise(), {
            loading: 'Uploading your bill...',
            success: 'Upload confirmed! Your bill is now being processed.',
            error: (err) => err.data?.error?.message || 'Upload failed. Please try again.',
            finally: () => setIsUploading(false),
        });
    };

    return (
        <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-8 mb-8 hover:border-primary-400 transition-colors">
            <div className="text-center">
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    className="hidden"
                    accept="application/pdf,image/jpeg,image/png"
                    disabled={isUploading}
                />
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-8 h-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Upload Your Bill
                </h3>
                <p className="text-gray-600 mb-6">
                    Drag and drop your PDF or image file, or click to browse
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <Button 
                        className="bg-primary-500 hover:bg-primary-600" 
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                    >
                        <Upload className="w-4 h-4 mr-2" />
                        {isUploading ? 'Uploading...' : 'Choose File'}
                    </Button>
                    <Button variant="outline" disabled={isUploading}>Enter Manually</Button>
                </div>
                <p className="text-sm text-gray-500 mt-4">
                    Supports PDF, JPG, PNG files up to 10MB
                </p>
            </div>
        </div>
    );
};
