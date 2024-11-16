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
