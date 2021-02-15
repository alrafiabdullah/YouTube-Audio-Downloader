from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage

from pytube import YouTube
from moviepy.editor import *

import os
import shutil

from .models import Temporary

# Create your views here.


def index(request):
    if request.method == "POST":
        try:
            shutil.rmtree("media/video")
        except:
            pass

        url = request.POST.get("url")
        if not "youtube" in url:
            messages.warning(request, 'Please enter a valid YouTube link!!!')
            return redirect("index")

        video_information = YouTube(url)
        tags = video_information.streams
        for tag in tags:
            if tag.mime_type == "video/mp4":
                video_file = video_information.streams.get_by_itag(tag.itag)
                video_file.download(output_path="media/video")
                break

        video_title = f"media/video/{video_information.title}.mp4"

        video = VideoFileClip(video_title)
        video.audio.write_audiofile(
            f"media/audio/{video_information.title}.mp3")

        song = Temporary.objects.create(
            name=video_information.title,
            audio=os.path.join(f"audio/{video_information.title}.mp3"),
        )

        song.save()

        messages.success(
            request, f"{video_information.title} converted successfully!")

        return HttpResponseRedirect(reverse("index"))

    audios = Temporary.objects.all().order_by("-downloaded_at")

    pagination = Paginator(audios, 5)
    page_number = request.GET.get("page", 1)

    try:
        page = pagination.page(page_number)
    except EmptyPage:
        page = pagination.page(1)

    context = {
        "audios": page,
        "total": Temporary.objects.count()
    }
    return render(request, "main/index.html", context)


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)

    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(
                fh.read(), content_type="application/audio")
            response["Content-Disposition"] = "inline;filename=" + \
                os.path.basename(file_path)
            return response

    raise Http404
