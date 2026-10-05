(() => {
  const root=document.documentElement, loader=document.getElementById('loader'), theme=document.getElementById('themeBtn');
  if(localStorage.getItem('sif-theme')==='dark') root.classList.add('dark');
  theme?.addEventListener('click',()=>{root.classList.toggle('dark');localStorage.setItem('sif-theme',root.classList.contains('dark')?'dark':'light')});
  window.addEventListener('load',()=>setTimeout(()=>loader?.classList.add('hide'),450));
  document.querySelectorAll('.sample').forEach(b=>b.addEventListener('click',()=>{const t=document.querySelector('textarea');if(t){t.value=b.dataset.text;t.focus()}}));
  document.querySelectorAll('form[data-loading]').forEach(f=>f.addEventListener('submit',()=>loader?.classList.remove('hide')));
})();
