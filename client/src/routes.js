import search from './components/Search';

export default [
   {
      path: '/',
      redirect: 'search'
   },
   {
      name: "search",
      path: "/search/:token?",
      component: search
   }
]