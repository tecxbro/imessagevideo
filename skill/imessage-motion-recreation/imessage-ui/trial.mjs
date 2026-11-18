export const trial = {
  title:'Night garden 🌙', duration:16, fps:30, width:1080, height:1920,
  participants:[
    {id:'self',name:'Nico',initials:'N',self:true},
    {id:'mina',name:'Mina Patel',initials:'MP',color:'#e3d4ed'},
    {id:'jo',name:'Jo Rivera',initials:'JR',color:'#d5e9df'}
  ],
  messages:[
    {id:'invite',senderId:'mina',at:0,copy:'The greenhouse opens after sunset. Should we bring the telescope? 🔭',reactions:[{ownerId:'jo',emoji:'❤️',at:1.5},{ownerId:'self',emoji:'👍',at:2}]},
    {id:'yes',senderId:'self',at:2.8,copy:'Yes! I found a quiet spot by the old observatory.',reactions:[{ownerId:'mina',emoji:'✨',at:3.5}]},
    {id:'cards',senderId:'jo',at:4.3,cards:[
      {title:'Under the stars',body:'Meet at the north entrance. Bring a warm layer.',symbol:'🌌',color:'#d4e1ed'},
      {title:'Moon garden',body:'A quiet path through the pale evening flowers.',symbol:'🌸',color:'#ead8df'},
      {title:'The glasshouse',body:'The last lantern tour begins at eight.',symbol:'🌿',color:'#d9e5d6'},
      {title:'A clear horizon',body:'Leave a little room for a detour.',symbol:'🔭',color:'#e9dfce'}
    ],switches:[{at:6,index:1},{at:7,index:2},{at:8,index:3}],reactions:[{ownerId:'self',emoji:'😍',at:9}]},
    {id:'send',senderId:'self',at:12,copy:'I’ll bring tea and the telescope. See you by the north gate! 🫖'},
    {id:'reply',senderId:'mina',at:13.5,copy:'Perfect. See you there 🌙'}
  ],
  composer:[{at:0,copy:''},{at:9.5,copy:'I’ll bring tea'},{at:10,copy:'I’ll bring tea and the telescope.'},{at:11,copy:'I’ll bring tea and the telescope. See you by the north gate! 🫖'},{at:12,copy:'',sendMessageId:'send'}],
  camera:[{at:0,x:0,y:0,scale:1},{at:4.8,x:-10,y:-40,scale:1.08},{at:8.5,x:8,y:-60,scale:1.08},{at:10,x:0,y:0,scale:1}]
};
