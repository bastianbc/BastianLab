from django.shortcuts import render, get_object_or_404, redirect
from .models import Article
from .forms import ArticleForm

def articles(request):

    search_query = request.GET.get('search', '')
    if search_query:
        articles = Article.objects.filter(title__icontains=search_query).order_by('-created_at')
    else:
        articles = Article.objects.filter(parent__isnull=True)

    return render(request, 'articles.html', {'articles': articles, 'search_query': search_query})

def view_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'view_article.html', {'article': article})

def new_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('articles')
    else:
        form = ArticleForm()
    return render(request, 'edit_article.html', locals())

def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('view-article', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'edit_article.html', locals())

def delete_article(request,slug):
    article = get_object_or_404(Article, slug=slug)
    article.delete()
    return redirect('articles')
