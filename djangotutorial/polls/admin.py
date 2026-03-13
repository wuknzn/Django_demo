from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Choice, Question, VoteReason


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ["question_text"]
    list_filter = ["pub_date"]
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        question = self.get_object(request, object_id)
        
        # 处理删除投票理由的请求
        if request.method == 'POST' and 'delete_reason' in request.POST:
            reason_id = request.POST.get('reason_id')
            if reason_id:
                try:
                    reason = VoteReason.objects.get(id=reason_id)
                    reason.delete()
                except VoteReason.DoesNotExist:
                    pass
            return HttpResponseRedirect(reverse('admin:polls_question_change', args=[object_id]))
        
        if question:
            choices = question.choice_set.all()
            choice_data = [(choice.choice_text, choice.votes) for choice in choices]
            extra_context['choice_data'] = choice_data
            
            # 按选项分组获取投票理由
            reasons_by_choice = {}
            for choice in choices:
                reasons = choice.votereason_set.all()
                if reasons:
                    reasons_by_choice[choice] = list(reasons)
            extra_context['reasons_by_choice'] = reasons_by_choice
        
        return super().change_view(request, object_id, form_url, extra_context)


admin.site.register(Question, QuestionAdmin)