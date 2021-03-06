from __future__ import absolute_import, unicode_literals

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.contrib.modeladmin.views import IndexView

from wagtail_personalisation.models import PersonalisablePage, Segment


class SegmentModelIndexView(IndexView):
    """Placeholder for additional dashboard functionality."""
    pass


@modeladmin_register
class SegmentModelAdmin(ModelAdmin):
    """The model admin for the Segments administration interface."""
    model = Segment
    index_view_class = SegmentModelIndexView
    menu_icon = 'group'
    add_to_settings_menu = False
    list_display = ('status', 'name', 'create_date', 'edit_date')
    index_view_extra_js = ['js/commons.js', 'js/index.js']
    index_view_extra_css = ['css/index.css']
    form_view_extra_js = ['js/commons.js', 'js/form.js']
    form_view_extra_css = ['css/form.css']


def toggle(request, segment_id):
    """Toggle the status of the selected segment.

    :param request: The http request
    :type request: django.http.HttpRequest
    :param segment_id: The primary key of the segment
    :type segment_id: int
    :returns: A redirect to the original page
    :rtype: django.http.HttpResponseRedirect

    """
    if request.user.has_perm('wagtailadmin.access_admin'):
        segment = get_object_or_404(Segment, pk=segment_id)

        if segment.status == 'enabled':
            segment.status = 'disabled'
        elif segment.status == 'disabled':
            segment.status = 'enabled'

        segment.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseForbidden()


def copy_page_view(request, page_id, segment_id):
    """Copy page with selected segment.

    :param request: The http request
    :type request: django.http.HttpRequest
    :param page_id: The primary key of the page
    :type segment_id: int
    :param segment_id: The primary key of the segment
    :type segment_id: int
    :returns: A redirect to the new page
    :rtype: django.http.HttpResponseRedirect

    """
    if request.user.has_perm('wagtailadmin.access_admin'):
        segment = get_object_or_404(Segment, pk=segment_id)
        page = get_object_or_404(PersonalisablePage, pk=page_id)

        slug = "{}-{}".format(page.slug, segment.encoded_name())
        title = "{} ({})".format(page.title, segment.name)
        update_attrs = {
            'title': title,
            'slug': slug,
            'segment': segment,
            'live': False,
            'canonical_page': page,
            'is_segmented': True,
        }

        new_page = page.copy(update_attrs=update_attrs, copy_revisions=False)

        edit_url = reverse('wagtailadmin_pages:edit', args=[new_page.id])

        return HttpResponseRedirect(edit_url)

    return HttpResponseForbidden()
