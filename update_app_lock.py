from pathlib import Path
import json

p = Path("public/index.html")
s = p.read_text()

if 'id="appLock"' in s:
    raise SystemExit("App Lock ya riga ya kasance. Ba a sake maimaita gyaran ba.")

# Add lock and setup screens before the main app
marker = '<div id="app">'
screens = r'''
<section id="appLock" style="display:none;min-height:100vh;align-items:center;justify-content:center;padding:25px;background:#f7f7ff">
  <div class="auth-card">
    <div class="logo">DAN AREWA DATA</div>
    <h2>Welcome back 👋</h2>
    <p class="sub" id="lockUserText">Enter your 5-digit app PIN to continue.</p>
    <form id="unlockForm">
      <div class="field">
        <label>5-digit App PIN</label>
        <input id="unlockPin" type="password" inputmode="numeric" maxlength="5"
          pattern="[0-9]{5}" required placeholder="•••••" autocomplete="off">
      </div>
      <button class="primary" type="submit">Unlock App</button>
    </form>
    <button id="fingerprintButton" class="action-btn"
      style="width:100%;margin-top:14px;display:none" type="button">
      🫆 Unlock with Fingerprint
    </button>
    <p style="text-align:center;margin-top:20px">
      <button class="link" type="button" id="switchAccount">Use another account</button>
    </p>
    <p class="notice">Your app PIN is different from your transaction PIN.</p>
  </div>
</section>

<section id="pinSetup" style="display:none;min-height:100vh;align-items:center;justify-content:center;padding:25px;background:#f7f7ff">
  <div class="auth-card">
    <div class="logo">DAN AREWA DATA</div>
    <h2>Create your App PIN 🔐</h2>
    <p class="sub">Create a 5-digit PIN. You will use it whenever you open the app.</p>
    <form id="setupPinForm">
      <div class="field">
        <label>New 5-digit App PIN</label>
        <input id="newAppPin" type="password" inputmode="numeric" maxlength="5"
          pattern="[0-9]{5}" required placeholder="•••••" autocomplete="new-password">
      </div>
      <div class="field">
        <label>Confirm 5-digit App PIN</label>
        <input id="confirmAppPin" type="password" inputmode="numeric" maxlength="5"
          pattern="[0-9]{5}" required placeholder="•••••" autocomplete="new-password">
      </div>
      <button class="primary" type="submit">Save App PIN</button>
    </form>
    <p class="notice">Keep your PIN private. This is a demo app security feature.</p>
  </div>
</section>
'''
if marker not in s:
    raise SystemExit("Ba a sami wurin app ba.")
s = s.replace(marker, screens + '\n' + marker, 1)

# Add biometric bundle before the existing application script
script_marker = '<script>\nconst $ = id => document.getElementById(id);'
if script_marker not in s:
    raise SystemExit("Ba a sami babban JavaScript ba.")
s = s.replace(script_marker, '<script src="biometric.js"></script>\n' + script_marker, 1)

# Update login success to require app PIN setup once
old = '''  current=email;
  sessionStorage.setItem("dan_arewa_3_session",email);
  enterApp();
});'''
new = '''  current=email;
  localStorage.setItem("dan_arewa_3_last_user",email);
  sessionStorage.setItem("dan_arewa_3_session",email);

  if(!users[email].unlockHash){
    $("auth").style.display="none";
    $("appLock").style.display="none";
    $("pinSetup").style.display="flex";
    $("newAppPin").value="";
    $("confirmAppPin").value="";
    return;
  }

  enterApp();
});'''
if old not in s:
    raise SystemExit("Ba a sami login success code ba.")
s = s.replace(old, new, 1)

# Add lock functions before enterApp
marker = 'function enterApp(){'
functions = r'''
let lockedEmail = null;

async function hashAppPin(pin){
  const bytes = new TextEncoder().encode(pin);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2,"0")).join("");
}

$("setupPinForm").addEventListener("submit", async e => {
  e.preventDefault();
  const a = $("newAppPin").value.trim();
  const b = $("confirmAppPin").value.trim();

  if(!/^[0-9]{5}$/.test(a)){
    toast("App PIN must contain exactly 5 digits");
    return;
  }
  if(a !== b){
    toast("The two PINs do not match");
    return;
  }

  users[current].unlockHash = await hashAppPin(a);
  saveUsers();
  localStorage.setItem("dan_arewa_3_last_user",current);
  $("pinSetup").style.display="none";
  enterApp();
});

$("unlockForm").addEventListener("submit", async e => {
  e.preventDefault();
  const pin = $("unlockPin").value.trim();
  if(!/^[0-9]{5}$/.test(pin)){
    toast("Enter your 5-digit App PIN");
    return;
  }

  const hash = await hashAppPin(pin);
  if(!lockedEmail || !users[lockedEmail] || users[lockedEmail].unlockHash !== hash){
    $("unlockPin").value="";
    toast("Incorrect App PIN");
    return;
  }

  current = lockedEmail;
  sessionStorage.setItem("dan_arewa_3_session",current);
  $("appLock").style.display="none";
  enterApp();
});

$("switchAccount").onclick = () => {
  localStorage.removeItem("dan_arewa_3_last_user");
  sessionStorage.removeItem("dan_arewa_3_session");
  lockedEmail = null;
  current = null;
  $("appLock").style.display="none";
  $("pinSetup").style.display="none";
  $("app").style.display="none";
  $("auth").style.display="flex";
};

async function prepareFingerprint(){
  const btn = $("fingerprintButton");
  btn.style.display = "none";

  if(!window.NativeBiometric || !window.Capacitor ||
     !window.Capacitor.isNativePlatform ||
     !window.Capacitor.isNativePlatform()) return;

  try{
    const result = await window.NativeBiometric.isAvailable();
    if(result && result.isAvailable) btn.style.display="block";
  }catch(e){
    btn.style.display="none";
  }
}

$("fingerprintButton").onclick = async () => {
  try{
    if(!window.NativeBiometric) throw new Error("Fingerprint plugin unavailable");
    await window.NativeBiometric.verifyIdentity({
      reason:"Unlock DAN AREWA DATA",
      title:"Fingerprint authentication",
      subtitle:"Verify your identity",
      description:"Use your fingerprint to open the app",
      negativeButtonText:"Use App PIN"
    });
    if(!lockedEmail || !users[lockedEmail]) return;
    current = lockedEmail;
    sessionStorage.setItem("dan_arewa_3_session",current);
    $("appLock").style.display="none";
    enterApp();
  }catch(e){
    toast("Fingerprint was not verified. Use your 5-digit PIN.");
  }
};

'''
if marker not in s:
    raise SystemExit("Ba a sami enterApp ba.")
s = s.replace(marker, functions + marker, 1)

# Logout returns to account selection/login
old = '''function logout(){
  current=null;
  sessionStorage.removeItem("dan_arewa_3_session");
  $("app").style.display="none";
  $("auth").style.display="flex";
  $("pin").value="";
}'''
new = '''function logout(){
  current=null;
  lockedEmail=null;
  localStorage.removeItem("dan_arewa_3_last_user");
  sessionStorage.removeItem("dan_arewa_3_session");
  $("app").style.display="none";
  $("appLock").style.display="none";
  $("pinSetup").style.display="none";
  $("auth").style.display="flex";
  $("pin").value="";
}'''
if old not in s:
    raise SystemExit("Ba a sami logout ba.")
s = s.replace(old, new, 1)

# Replace startup logic
old = '''authMode();
if(current&&users[current])enterApp();'''
new = '''authMode();
current = null;
sessionStorage.removeItem("dan_arewa_3_session");

const rememberedEmail = localStorage.getItem("dan_arewa_3_last_user");
if(rememberedEmail && users[rememberedEmail] && users[rememberedEmail].unlockHash){
  lockedEmail = rememberedEmail;
  $("auth").style.display="none";
  $("app").style.display="none";
  $("appLock").style.display="flex";
  $("lockUserText").textContent =
    "Hello " + users[rememberedEmail].name + ". Enter your 5-digit App PIN.";
  prepareFingerprint();
}else{
  $("appLock").style.display="none";
  $("pinSetup").style.display="none";
  $("auth").style.display="flex";
}'''
if old not in s:
    raise SystemExit("Ba a sami startup code ba.")
s = s.replace(old, new, 1)

p.write_text(s)
print("An saka 5-digit App PIN da lock screen.")
