(this.webpackJsonprechart_react=this.webpackJsonprechart_react||[]).push([[0],{98:function(t,e,n){"use strict";n.r(e);var a=n(1),c=n(0),r=n(35),i=n.n(r),s=n(24),o=n(30),l=n(57),j=n.n(l),h=n(33),d=n.n(h),b=n(45),u="GET_DATA",p="GET_STATUS_CLOSED",O="GET_STATUS_OPENED",g=n(46),x=n.n(g),f=function(t){var e=("http://localhost:3000"===window.location.origin||"http://127.0.0.1:3000"===window.location.origin?"http://localhost:8000/notify/forrechart/":window.location.origin+"/notify/forrechart/")+t;return function(){var t=Object(b.a)(d.a.mark((function t(n){var a;return d.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,x()(e);case 3:a=t.sent,n({type:p,payload:a.data.closed}),n({type:O,payload:a.data.opened}),t.next=12;break;case 8:t.prev=8,t.t0=t.catch(0),n({type:p,payload:[]}),n({type:O,payload:[]});case 12:case"end":return t.stop()}}),t,null,[[0,8]])})));return function(e){return t.apply(this,arguments)}}()};var v=function(t){var e=Object(s.b)(),n={series:[{name:"Online",data:Object(s.c)((function(t){return t.statData.data}))}],options:{chart:{height:380,width:"100%",type:"area",toolbar:{show:!1}},xaxis:{type:"datetime"},stroke:{curve:"smooth",width:1},title:{text:"Connections user",align:"left"},markers:{size:0,shape:"square"}}};return Object(c.useEffect)((function(){e(function(t){var e=("http://localhost:3000"===window.location.origin||"http://127.0.0.1:3000"===window.location.origin?"http://localhost:8000/stat/":window.location.origin+"/stat/")+t;return function(){var t=Object(b.a)(d.a.mark((function t(n){var a;return d.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,x()(e);case 3:a=t.sent,n({type:u,payload:a.data}),t.next=10;break;case 7:t.prev=7,t.t0=t.catch(0),n({type:u,payload:[]});case 10:case"end":return t.stop()}}),t,null,[[0,7]])})));return function(e){return t.apply(this,arguments)}}()}(t.token))}),[]),Object(a.jsx)(j.a,{options:n.options,series:n.series,type:"line",height:350})},w=n(118),y=n(117),m=n(115),_=n(116),k=n(120),D=n(114),E=n(119),T=function(t){var e=new Date(t).getDate(),n=new Date(t).getMonth()+1,a=new Date(t).getHours(),c=new Date(t).getMinutes(),r=new Date(t).getSeconds();return"".concat(n,"/").concat(e," ").concat(a,":").concat(c,":").concat(r)};var C=function(t){var e=Object(s.b)(),n=Object(s.c)((function(t){return t.statusConnections.opened}));return Object(c.useEffect)((function(){e(f(t.token))}),[]),Object(a.jsx)(w.a,{component:y.a,children:Object(a.jsxs)(m.a,{sx:{minWidth:650},size:"small","aria-label":"a dense table",children:[Object(a.jsxs)(_.a,{children:[Object(a.jsx)(k.a,{children:Object(a.jsx)(D.a,{align:"center",colSpan:5,children:"Active Connections"})}),Object(a.jsxs)(k.a,{children:[Object(a.jsx)(D.a,{children:"Id Channel"}),Object(a.jsx)(D.a,{align:"right",children:"Type"}),Object(a.jsx)(D.a,{align:"right",children:"Ip"}),Object(a.jsx)(D.a,{align:"right",children:"User Agent"}),Object(a.jsx)(D.a,{align:"right",children:"Start"})]})]}),Object(a.jsx)(E.a,{children:n.map((function(t){return Object(a.jsxs)(k.a,{sx:{"&:last-child td, &:last-child th":{border:0}},children:[Object(a.jsx)(D.a,{component:"th",scope:"row",children:t.media}),Object(a.jsx)(D.a,{align:"right",children:t.type}),Object(a.jsx)(D.a,{align:"right",children:t.ip}),Object(a.jsx)(D.a,{align:"right",children:t.user_agent.length>30?t.user_agent.slice(0,30)+"...":t.user_agent}),Object(a.jsx)(D.a,{align:"right",children:T(t.created_at)})]},t.id)}))})]})})};var S=function(t){var e=Object(s.b)(),n=Object(s.c)((function(t){return t.statusConnections.closed}));return Object(c.useEffect)((function(){e(f(t.token))}),[]),Object(a.jsx)(w.a,{component:y.a,children:Object(a.jsxs)(m.a,{sx:{minWidth:650},size:"small","aria-label":"customized table",children:[Object(a.jsxs)(_.a,{children:[Object(a.jsx)(k.a,{children:Object(a.jsx)(D.a,{align:"center",colSpan:5,children:"History Connections"})}),Object(a.jsxs)(k.a,{children:[Object(a.jsx)(D.a,{children:"Id Channel"}),Object(a.jsx)(D.a,{align:"right",children:"Type"}),Object(a.jsx)(D.a,{align:"right",children:"Ip"}),Object(a.jsx)(D.a,{align:"right",children:"User Agent"}),Object(a.jsx)(D.a,{align:"right",children:"End"})]})]}),Object(a.jsx)(E.a,{children:n.map((function(t){return Object(a.jsxs)(k.a,{sx:{"&:last-child td, &:last-child th":{border:0}},children:[Object(a.jsx)(D.a,{component:"th",scope:"row",children:t.media}),Object(a.jsx)(D.a,{align:"right",children:t.type}),Object(a.jsx)(D.a,{align:"right",children:t.ip}),Object(a.jsx)(D.a,{align:"right",children:t.user_agent.length>30?t.user_agent.slice(0,30)+"...":t.user_agent}),Object(a.jsx)(D.a,{align:"right",children:T(t.deleted_at)})]},t.id)}))})]})})},A=n(112);var I=function(t){var e=t.match.params.data;return Object(a.jsxs)(a.Fragment,{children:[Object(a.jsx)(v,{token:e}),Object(a.jsxs)(A.a,{container:!0,spacing:1,children:[Object(a.jsx)(A.a,{item:!0,xs:12,lg:6,children:Object(a.jsx)(C,{token:e})}),Object(a.jsx)(A.a,{item:!0,xs:12,lg:6,children:Object(a.jsx)(S,{token:e})})]})]})},z=n(62),U=n(7),G=n(61),H=n(25),J={data:[]},M={closed:[],opened:[]},W=Object(o.b)({statData:function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:J,e=arguments.length>1?arguments[1]:void 0;switch(e.type){case u:return Object(H.a)(Object(H.a)({},t),{},{data:e.payload});default:return t}},statusConnections:function(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:M,e=arguments.length>1?arguments[1]:void 0;switch(e.type){case p:return Object(H.a)(Object(H.a)({},t),{},{closed:e.payload});case O:return Object(H.a)(Object(H.a)({},t),{},{opened:e.payload});default:return t}}}),q=Object(o.d)(W,Object(o.c)(Object(o.a)(G.a)));i.a.render(Object(a.jsx)(s.a,{store:q,children:Object(a.jsx)(z.a,{children:Object(a.jsx)(U.c,{children:Object(a.jsx)(U.a,{exact:!0,path:"/:data",component:I})})})}),document.getElementById("root"))}},[[98,1,2]]]);
//# sourceMappingURL=main.78dba6e3.chunk.js.map