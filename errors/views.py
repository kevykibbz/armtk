from django.shortcuts import render

def error_400(request,exception):
	return render(request,'manager/400.html',{'title':'Error | Bad Request'},status=400)

def error_403(request,exception):
	return render(request,'manager/403.html',{'title':'Error | Access Forbidden'},status=403)

def error_404(request,exception):
	return render(request,'manager/404.html',{'title':'Error | Page Not Found'},status=404)

def error_500(request,*args,**argv):
	return render(request,'manager/500.html',{'title':'Error | Internal Server Error'},status=500)

