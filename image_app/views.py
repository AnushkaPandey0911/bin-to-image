from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from PIL import Image
import os
import datetime
from django.conf import settings

BIN_PATH = 'media/sample.bin'
IMAGE_PATH = 'media/generated_image.png'
UPLOAD_PATH = 'media/uploaded.bin'

def index(request):
    image_path = request.session.get('image_path')
    return render(request, 'image_app/index.html', {'image_path': image_path})

def generate_bin(request):
    data = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    data.tofile(BIN_PATH)
    return HttpResponseRedirect('/')

@csrf_exempt

def generate_image(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        pattern_type = request.POST.get('pattern_type', 'random')
        size = int(request.POST.get('image_size', 100))
        shape = (size, size)

        data = None

        if source == 'generated':
            if not os.path.exists(BIN_PATH):
                return JsonResponse({'error': 'Generated BIN file not found.'}, status=404)
            data = np.fromfile(BIN_PATH, dtype=np.uint8)
            if data.size < size * size:
                return JsonResponse({'error': 'BIN file too small for selected size.'}, status=400)
            data = data[:size * size].reshape(shape)

        elif source == 'upload':
            uploaded_file = request.FILES.get('bin_file')
            if uploaded_file:
                with open(UPLOAD_PATH, 'wb+') as dest:
                    for chunk in uploaded_file.chunks():
                        dest.write(chunk)
                data = np.fromfile(UPLOAD_PATH, dtype=np.uint8)
                if data.size < size * size:
                    return JsonResponse({'error': 'Uploaded BIN file too small for selected size.'}, status=400)
                data = data[:size * size].reshape(shape)
            else:
                return JsonResponse({'error': 'No file uploaded.'}, status=400)

        elif source == 'pattern':
            data = np.zeros(shape, dtype=np.uint8)

            if pattern_type == 'checkerboard':
                for i in range(size):
                    for j in range(size):
                        data[i, j] = 255 if (i + j) % 2 == 0 else 0

            elif pattern_type == 'diagonal':
                for i in range(size):
                    for j in range(size):
                        data[i, j] = 255 if (i == j or i + j == size - 1) else 0

            elif pattern_type == 'horizontal_lines':
                for i in range(size):
                    value = 255 if i % 10 < 5 else 0
                    data[i, :] = value

            elif pattern_type == 'vertical_lines':
                for j in range(size):
                    value = 255 if j % 10 < 5 else 0
                    data[:, j] = value

            elif pattern_type == 'diamond':
                for i in range(size):
                    for j in range(size):
                        if abs(i - size // 2) + abs(j - size // 2) < size // 2:
                            data[i, j] = 255
                        else:
                            data[i, j] = 0

            else:  # random noise fallback
                data = np.random.randint(0, 256, shape, dtype=np.uint8)

        else:
            return JsonResponse({'error': 'Invalid source.'}, status=400)

        image = Image.fromarray(data, 'L')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"output_image_{timestamp}.png"
        image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
        image.save(image_path)

        # Save this in session for later retrieval on index page
        request.session['image_path'] = f"media/{image_filename}"

        return HttpResponseRedirect('/')


    return JsonResponse({'error': 'POST method required.'}, status=405)

