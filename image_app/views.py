from PIL import Image, ImageFilter
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImageUploadForm
from .models import UploadedImage


def index(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("image_app:index")
    else:
        form = ImageUploadForm()

    images = UploadedImage.objects.all().order_by("-uploaded_at")
    return render(request, "image_app/index.html", {"form": form, "images": images})


def threshold_image(image_path, threshold=128):
    image = Image.open(image_path).convert("L")
    image = image.point(lambda p: p > threshold and 255)
    return image


def otsu_threshold_image(image_path):
    image = Image.open(image_path).convert("L")
    histogram = image.histogram()

    total_pixels = sum(histogram)
    current_max, threshold = 0, 0
    sum_total, sum_background = 0, 0

    for i in range(256):
        sum_total += i * histogram[i]

    weight_background = 0
    for i in range(256):
        weight_background += histogram[i]
        if weight_background == 0:
            continue

        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break

        sum_background += i * histogram[i]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground

        between_class_variance = (
            weight_background
            * weight_foreground
            * (mean_background - mean_foreground) ** 2
        )

        if between_class_variance > current_max:
            current_max = between_class_variance
            threshold = i

    thresholded_image = image.point(lambda p: 255 if p > threshold else 0)
    return thresholded_image


def smooth_image(image_path):
    image = Image.open(image_path)
    image = image.filter(ImageFilter.GaussianBlur(radius=2))
    return image


def process_image(request, image_id):
    image_obj = get_object_or_404(UploadedImage, id=image_id)
    processed_image = None
    processed_image_path = None

    if request.method == "POST":
        if "threshold" in request.POST:
            threshold = int(request.POST.get("threshold", 128))
            processed_image = threshold_image(image_obj.image.path, threshold)
        elif "otsu" in request.POST:
            processed_image = otsu_threshold_image(image_obj.image.path)
        elif "smooth" in request.POST:
            processed_image = smooth_image(image_obj.image.path)

        if processed_image:
            processed_image_path = f"media/images/processed_image_{image_obj.id}.png"
            processed_image.save(processed_image_path)

    return render(
        request,
        "image_app/process_image.html",
        {"image": image_obj, "processed_image_url": processed_image_path},
    )
