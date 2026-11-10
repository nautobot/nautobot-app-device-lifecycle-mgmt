"""QR codes that open the Nautobot detail page of a device."""

import io

import segno
from django.utils.text import slugify

QR_ERROR_CORRECTION = "m"
QR_CONTENT_TYPES = {"png": "image/png", "svg": "image/svg+xml"}


def get_device_url(request, device):
    """Return the absolute URL of the device detail page, which is what the QR code encodes."""
    return request.build_absolute_uri(device.get_absolute_url())


def make_device_qr_code(request, device):
    """Return the QR code for the device detail page."""
    return segno.make_qr(get_device_url(request, device), error=QR_ERROR_CORRECTION)


def get_device_qr_code_data_uri(request, device):
    """Return the device QR code as an SVG data URI, sized by the img tag that displays it."""
    return make_device_qr_code(request, device).svg_data_uri(border=2, omitsize=True)


def get_device_qr_code_file(request, device, image_format="svg"):
    """Return the device QR code as (content, content type, file name) for downloading."""
    buffer = io.BytesIO()
    make_device_qr_code(request, device).save(buffer, kind=image_format, scale=10, border=4)
    file_name = f"{slugify(device.name) or device.pk}-qr.{image_format}"
    return buffer.getvalue(), QR_CONTENT_TYPES[image_format], file_name
