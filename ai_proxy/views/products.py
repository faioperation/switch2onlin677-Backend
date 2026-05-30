from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ai_proxy.schemas import products as sc
from .base import BaseAIProxyView


class ProductTemplateProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Get product upload template",
        operation_description="Returns the column schema so the frontend can generate a downloadable template spreadsheet.",
        tags=["AI Proxy - Products Upload"],
        responses={200: sc.UPLOAD_TEMPLATE_RESPONSE},
    )
    def get(self, request):
        return self.proxy_request("GET", "/products/upload-template")


class ProductUploadProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Upload products via Excel or CSV",
        operation_description="""
Accept an Excel (.xlsx) or CSV (.csv) file, validate it, create an upload job, and process it asynchronously.

**File Rules:**
- Max size: 10 MB
- Max rows: 10,000
- Extensions: `.xlsx` or `.csv`

**Key Columns:** `barcode` (required), plus optional fields: `item_name`, `brand_name`, `category_name`, `subcategory_name`, `price`, `available_qty`, `product_status`, `is_best_selling`, `is_new_arrival`, etc.

Use `dry_run=true` to validate without persisting any changes.

Poll `GET /products/uploads/{job_id}` for progress after submission.
""",
        tags=["AI Proxy - Products Upload"],
        manual_parameters=sc.PRODUCT_UPLOAD_PARAMETERS,
        request_body=sc.PRODUCT_UPLOAD_REQUEST,
        responses={202: sc.PRODUCT_UPLOAD_RESPONSE},
    )
    def post(self, request):
        files = {
            k: (v.name, v.read(), v.content_type) for k, v in request.FILES.items()
        }
        data = {k: v for k, v in request.data.items() if k not in request.FILES}
        return self.proxy_request(
            "POST",
            "/products/upload",
            data=data,
            files=files,
            params=request.query_params,
            timeout=300,
        )


class ProductUploadJobDetailProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Get upload job status",
        operation_description="""
Poll the status and progress of a specific upload job.

**Status flow:** `queued → processing → completed | failed`
""",
        tags=["AI Proxy - Products Upload"],
        responses={200: sc.UPLOAD_JOB_DETAIL_RESPONSE},
    )
    def get(self, request, job_id):
        return self.proxy_request("GET", f"/products/uploads/{job_id}")


class ProductUploadJobListProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="List all upload jobs",
        operation_description="Paginated list of all past upload jobs (newest first). Used by operations dashboards and audit trails.",
        tags=["AI Proxy - Products Upload"],
        manual_parameters=sc.UPLOAD_JOB_LIST_PARAMETERS,
        responses={200: sc.UPLOAD_JOB_LIST_RESPONSE},
    )
    def get(self, request):
        return self.proxy_request("GET", "/products/uploads", params=request.query_params)


class ProductFilterProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Get product filters",
        tags=["AI Proxy - Products"],
    )
    def get(self, request):
        return self.proxy_request("GET", "/products/filters", params=request.query_params)


class ProductListProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="List Products",
        operation_description="List, search, filter and paginate products.",
        tags=["AI Proxy - Products"],
        manual_parameters=sc.PRODUCT_LIST_PARAMETERS,
        responses={200: sc.PRODUCT_LIST_RESPONSE},
    )
    def get(self, request):
        return self.proxy_request("GET", "/products", params=request.query_params)


class ProductDetailProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Get product by barcode",
        tags=["AI Proxy - Products Barcode"],
    )
    def get(self, request, barcode):
        return self.proxy_request("GET", f"/products/{barcode}")

    @swagger_auto_schema(
        operation_summary="Update product by barcode",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "price": openapi.Schema(type=openapi.TYPE_NUMBER),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "category": openapi.Schema(type=openapi.TYPE_STRING),
                "stock": openapi.Schema(type=openapi.TYPE_INTEGER),
                "image_url": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        tags=["AI Proxy - Products Barcode"],
    )
    def put(self, request, barcode):
        return self.proxy_request("PUT", f"/products/{barcode}", data=request.data)

    @swagger_auto_schema(
        operation_summary="Soft-delete product by barcode",
        operation_description="Sets `deleted_at` timestamp; the product row is retained in the database. Excluded from all public-facing queries immediately. Restore with `POST /products/{barcode}/restore`.",
        tags=["AI Proxy - Products Barcode"],
        responses={200: sc.PRODUCT_DELETE_RESPONSE},
    )
    def delete(self, request, barcode):
        return self.proxy_request("DELETE", f"/products/{barcode}")


class ProductRestoreProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Restore soft-deleted product",
        operation_description="""
Restore a soft-deleted product by clearing its `deleted_at` timestamp.

| HTTP Code | Condition |
|---|---|
| 200 | Restored successfully |
| 404 | Product row does not exist |
| 422 | Product is not currently in a deleted state |
| 500 | Database commit failure |
""",
        tags=["AI Proxy - Products Barcode"],
        responses={200: sc.PRODUCT_RESTORE_RESPONSE},
    )
    def post(self, request, barcode):
        return self.proxy_request("POST", f"/products/{barcode}/restore")


class ProductStatusProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Transition product status",
        operation_description="""
Transition a product to a new status with full audit logging.

**Allowed transitions:**

| From | To | Allowed |
|---|---|---|
| draft | active | Yes |
| draft | inactive | Yes |
| active | draft | Yes |
| active | inactive | Yes |
| inactive | active | Yes |
| inactive | draft | No — re-activate first |
""",
        tags=["AI Proxy - Products Barcode"],
        request_body=sc.PRODUCT_STATUS_REQUEST,
        responses={200: sc.PRODUCT_STATUS_RESPONSE},
    )
    def patch(self, request, barcode):
        return self.proxy_request("PATCH", f"/products/{barcode}/status", data=request.data)


class ProductBulkStatusProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Bulk transition product status",
        operation_description="Transition up to 500 products to a new status in one request. Valid and invalid products are processed independently.",
        tags=["AI Proxy - Products Bulk"],
        request_body=sc.PRODUCT_BULK_STATUS_REQUEST,
        responses={200: sc.PRODUCT_BULK_STATUS_RESPONSE},
    )
    def post(self, request):
        return self.proxy_request("POST", "/products/bulk/status", data=request.data)


class ProductFlagsProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Update product editorial flags",
        operation_description="Update editorial and recommendation flags for a single product. All fields are optional — only supplied fields are changed. SAP sync will never overwrite these fields.",
        tags=["AI Proxy - Products Barcode"],
        request_body=sc.PRODUCT_FLAGS_REQUEST,
        responses={200: sc.PRODUCT_FLAGS_RESPONSE},
    )
    def patch(self, request, barcode):
        return self.proxy_request("PATCH", f"/products/{barcode}/flags", data=request.data)


class ProductBulkFlagsProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Bulk update product editorial flags",
        operation_description="Apply the same editorial flags to up to 500 products at once. Products not found are listed in `not_found` but do not fail the request.",
        tags=["AI Proxy - Products Bulk"],
        request_body=sc.PRODUCT_BULK_FLAGS_REQUEST,
        responses={200: sc.PRODUCT_BULK_FLAGS_RESPONSE},
    )
    def post(self, request):
        return self.proxy_request("POST", "/products/bulk/flags", data=request.data)


class ProductEmbeddingRefreshProxyView(BaseAIProxyView):
    @swagger_auto_schema(
        operation_summary="Refresh embedding for a single product",
        operation_description="""
Immediately re-generate the embedding for a single product.

Use after editing a product's **name, description, or tags**.

Runs **synchronously** — returns the new `embedding_updated_at` timestamp.
""",
        tags=["AI Proxy - Embeddings"],
        responses={200: sc.PRODUCT_EMBEDDING_REFRESH_RESPONSE},
    )
    def patch(self, request, barcode):
        return self.proxy_request("PATCH", f"/products/{barcode}/embedding/refresh")
