// ======================================================
// HEALTH AI
// Premium Medical Background
// Part 1/3
// ======================================================

(() => {

"use strict";

// ---------------------------------------
// Canvas
// ---------------------------------------

const canvas = document.getElementById("dnaCanvas") || document.createElement("canvas");

if(!canvas.id){
    canvas.id="dnaCanvas";
    document.body.prepend(canvas);
}

const ctx = canvas.getContext("2d");

canvas.style.position="fixed";
canvas.style.top="0";
canvas.style.left="0";
canvas.style.width="100%";
canvas.style.height="100%";
canvas.style.pointerEvents="none";
canvas.style.zIndex="-10";

let w,h,dpr;

function resize(){

    w=window.innerWidth;
    h=window.innerHeight;

    dpr=Math.min(window.devicePixelRatio||1,2);

    canvas.width=w*dpr;
    canvas.height=h*dpr;

    ctx.setTransform(dpr,0,0,dpr,0,0);

}

window.addEventListener("resize",resize);
resize();


// ---------------------------------------
// Helpers
// ---------------------------------------

function lerp(a,b,t){
    return a+(b-a)*t;
}

function clamp(v,min,max){
    return Math.max(min,Math.min(max,v));
}


// ---------------------------------------
// Floating Particles
// ---------------------------------------

const particles=[];

const PARTICLE_COUNT=170;

for(let i=0;i<PARTICLE_COUNT;i++){

    particles.push({

        x:Math.random()*w,

        y:Math.random()*h,

        r:Math.random()*2+0.5,

        speed:0.2+Math.random()*0.8,

        alpha:0.2+Math.random()*0.6

    });

}

function drawParticles(){

    ctx.save();

    particles.forEach(p=>{

        p.y-=p.speed;

        if(p.y<0){

            p.y=h+20;
            p.x=Math.random()*w;

        }

        ctx.beginPath();

        ctx.fillStyle=`rgba(110,230,255,${p.alpha})`;

        ctx.shadowBlur=12;
        ctx.shadowColor="#00d4ff";

        ctx.arc(
            p.x,
            p.y,
            p.r,
            0,
            Math.PI*2
        );

        ctx.fill();

    });

    ctx.restore();

}


// ---------------------------------------
// Background Glow
// ---------------------------------------

function drawBackgroundGlow(){

    const g=ctx.createRadialGradient(

        w/2,
        h/2,
        100,

        w/2,
        h/2,
        700

    );

    g.addColorStop(0,"rgba(0,180,255,.22)");
    g.addColorStop(.5,"rgba(0,90,180,.08)");
    g.addColorStop(1,"rgba(0,0,0,0)");

    ctx.fillStyle=g;

    ctx.fillRect(0,0,w,h);

}


// ---------------------------------------
// DNA Variables
// ---------------------------------------

let dnaRotation=0;

const dnaHeight=520;
const dnaSpacing=13;
const dnaRadius=78;
// ---------------------------------------
// Draw 3D DNA Helix
// ---------------------------------------

function drawDNA(offsetX){

    ctx.save();

    ctx.translate(
        w/2 + offsetX,
        h/2
    );

    for(let y=-dnaHeight/2;y<=dnaHeight/2;y+=dnaSpacing){

        const angle = y*0.045 + dnaRotation;

        const x1 = Math.sin(angle)*dnaRadius;
        const x2 = -Math.sin(angle)*dnaRadius;

        const depth = (Math.cos(angle)+1)/2;

        // Connection
        ctx.beginPath();
        ctx.moveTo(x1,y);
        ctx.lineTo(x2,y);

        ctx.lineWidth=1.2;

        ctx.strokeStyle=
        `rgba(0,210,255,${0.15+depth*0.35})`;

        ctx.stroke();

        // Left Node
ctx.beginPath();
ctx.fillStyle=
`rgba(140,240,255,${0.35+depth*0.65})`;

ctx.shadowBlur=18;
ctx.shadowColor="#15bee0";

ctx.arc(
    x1,
    y,
    3.5+depth*2.5,
    0,
    Math.PI*2
);

ctx.fill();

// Right Node
ctx.beginPath();

ctx.arc(
    x2,
    y,
    3.5+depth*2.5,
    0,
    Math.PI*2
);

ctx.fill();
    }

    ctx.restore();

}

// ---------------------------------------
// Anatomical Wireframe Heart
// ---------------------------------------

let heartRotation=0;

function drawHeart(){

    ctx.save();

    ctx.translate(
        w/2,
        h/2
    );

    heartRotation+=0.008;

    ctx.rotate(heartRotation);

    ctx.scale(1.18,1.18);

    ctx.beginPath();

    for(let t=0;t<=Math.PI*2;t+=0.015){

        const x=
        16*Math.pow(Math.sin(t),3);

        const y=
        -(13*Math.cos(t)
        -5*Math.cos(2*t)
        -2*Math.cos(3*t)
        -Math.cos(4*t));

        if(t===0){

            ctx.moveTo(
                x*7,
                y*7
            );

        }else{

            ctx.lineTo(
                x*7,
                y*7
            );

        }

    }

    ctx.closePath();

    ctx.lineWidth=2;

    ctx.strokeStyle="rgba(0,220,255,.95)";

    ctx.shadowBlur=30;
    ctx.shadowColor="#00d4ff";

    ctx.stroke();

    // Internal sketch lines

    ctx.beginPath();

    ctx.moveTo(-35,-55);
    ctx.lineTo(0,-10);
    ctx.lineTo(28,-58);

    ctx.moveTo(-22,-10);
    ctx.lineTo(22,30);

    ctx.moveTo(-8,-5);
    ctx.lineTo(10,55);

    ctx.strokeStyle="rgba(180,245,255,.55)";
    ctx.lineWidth=1;

    ctx.stroke();

    ctx.restore();

}

// ---------------------------------------
// Animation Variable
// ---------------------------------------

let lastTime=0;
// ---------------------------------------
// Main Animation Loop
// ---------------------------------------

function animate(time){

    const delta = time - lastTime;
    lastTime = time;

    // Clear canvas
    ctx.clearRect(0,0,w,h);

    // Background glow
    drawBackgroundGlow();

    // Floating particles
    drawParticles();

    // Rotate DNA
    dnaRotation += 0.012;

    // Draw two DNA helices
    drawDNA(-260);
    drawDNA(260);

    // Draw rotating anatomical heart
    drawHeart();

    // Soft center glow
    const glow = ctx.createRadialGradient(
        w/2,
        h/2,
        50,
        w/2,
        h/2,
        350
    );

    glow.addColorStop(0,"rgba(0,212,255,0.08)");
    glow.addColorStop(0.5,"rgba(0,150,255,0.03)");
    glow.addColorStop(1,"rgba(0,0,0,0)");

    ctx.fillStyle = glow;
    ctx.fillRect(0,0,w,h);

    requestAnimationFrame(animate);

}

// ---------------------------------------
// Start Animation
// ---------------------------------------

requestAnimationFrame(animate);

})()