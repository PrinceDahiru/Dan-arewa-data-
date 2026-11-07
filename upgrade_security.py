from pathlib import Path

p = Path("public/index.html")
s = p.read_text()

def replace(old, new, label):
    global s
    if old not in s:
        raise SystemExit("AN GAGARA: Ba a sami wurin " + label + " ba. Babu wani canji da aka ajiye.")
    s = s.replace(old, new, 1)
    print("OK:", label)

# 1. Login PIN mai lambobi shida
replace(
'''<div class="field"><label>Password</label><input id="password" type="password" placeholder="Enter password" required minlength="4"></div>''',
'''<div class="field"><label>6-Digit Login PIN</label><input id="password" type="password" inputmode="numeric" maxlength="6" pattern="[0-9]{6}" placeholder="Enter 6-digit PIN" required minlength="6"></div>
   <div class="field" id="transactionPinField" style="display:none"><label>4-Digit Transaction PIN</label><input id="transactionPin" type="password" inputmode="numeric" maxlength="4" pattern="[0-9]{4}" placeholder="Create 4-digit PIN"></div>''',
"Login PIN da Transaction PIN"
)

# 2. Fingerprint button a login
replace(
'''  </form>
  <div class="authswitch">''',
'''  </form>
  <button class="secondary full" type="button" id="fingerLogin" style="margin-top:12px">☝ Use Fingerprint</button>
  <div class="authswitch">''',
"Fingerprint login button"
)

# 3. Fingerprint setup a profile
replace(
'''  <button class="secondary full" id="profileLogout">Logout</button>''',
'''  <button class="primary full" id="enableFingerprint" style="margin-bottom:12px">☝ Enable Fingerprint Login</button>
  <button class="secondary full" id="profileLogout">Logout</button>''',
"Fingerprint setup"
)

# 4. Auth mode
replace(
''' $('fullName').required=register;
 $('authSubmit').textContent=register?'Create Account':'Sign In';''',
''' $('fullName').required=register;
 $('transactionPinField').style.display=register?'block':'none';
 $('transactionPin').required=register;
 $('authSubmit').textContent=register?'Create Account':'Sign In';''',
"Registration PIN display"
)

# 5. Store both PINs during registration
replace(
'''  users[email]={name:$('fullName').value.trim(),password:pass,balance:10000,transactions:[]};''',
'''  const tp=$('transactionPin').value;
  if(!/^\\d{6}$/.test(pass))return notify('Login PIN must contain 6 digits');
  if(!/^\\d{4}$/.test(tp))return notify('Transaction PIN must contain 4 digits');
  users[email]={name:$('fullName').value.trim(),password:pass,transactionPin:tp,balance:10000,transactions:[]};''',
"Save security PINs"
)

# 6. Login validation
replace(
'''  if(!users[email]||users[email].password!==pass)return notify('Invalid email or password');
  current=email;''',
'''  if(!/^\\d{6}$/.test(pass))return notify('Login PIN must contain 6 digits');
  if(!users[email]||users[email].password!==pass)return notify('Invalid email or PIN');
  current=email;''',
"Login PIN verification"
)

# 7. Transaction PIN verification
replace(
''' const p=prices[$('network').value][selected];
 const transaction={network:$('network').value,plan:p[0],phone,amount:p[1],date:new Date().toLocaleString()};''',
''' const pin=prompt('Enter your 4-digit Transaction PIN');
 if(pin===null)return;
 if(!/^\\d{4}$/.test(pin))return notify('Transaction PIN must contain 4 digits');
 if(pin!==users[current].transactionPin)return notify('Incorrect Transaction PIN');
 const p=prices[$('network').value][selected];
 const transaction={network:$('network').value,plan:p[0],phone,amount:p[1],date:new Date().toLocaleString()};''',
"Transaction PIN verification"
)

# 8. Fingerprint functionality
marker = "$('authToggle').onclick=()=>{register=!register;authMode()};"

fingerprint = r'''
function b64url(buffer){
 return btoa(String.fromCharCode(...new Uint8Array(buffer)))
  .replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
function fromB64url(value){
 value=value.replace(/-/g,'+').replace(/_/g,'/');
 value+='='.repeat((4-value.length%4)%4);
 return Uint8Array.from(atob(value),c=>c.charCodeAt(0));
}
function randomChallenge(){
 const a=new Uint8Array(32);
 crypto.getRandomValues(a);
 return a;
}
async function enableFingerprint(){
 try{
  if(!window.PublicKeyCredential || !navigator.credentials)
   return notify('Fingerprint is not supported in this browser');
  if(!window.isSecureContext)
   return notify('Open the app through localhost HTTPS or localhost');
  const name=users[current].name;
  const credential=await navigator.credentials.create({publicKey:{
   challenge:randomChallenge(),
   rp:{name:'DAN AREWA DATA',id:location.hostname},
   user:{id:new TextEncoder().encode(current),name:current,displayName:name},
   pubKeyCredParams:[{type:'public-key',alg:-7},{type:'public-key',alg:-257}],
   authenticatorSelection:{
    authenticatorAttachment:'platform',
    userVerification:'required',
    residentKey:'preferred'
   },
   timeout:60000,
   attestation:'none'
  }});
  if(!credential)return notify('Fingerprint setup cancelled');
  localStorage.setItem('da_bio',JSON.stringify({
   email:current,id:b64url(credential.rawId)
  }));
  notify('Fingerprint login enabled successfully');
 }catch(e){
  notify('Fingerprint setup failed: '+(e.message||'Try again'));
 }
}
$('enableFingerprint').onclick=enableFingerprint;

$('fingerLogin').onclick=async()=>{
 try{
  const record=JSON.parse(localStorage.getItem('da_bio')||'null');
  if(!record)return notify('Enable fingerprint first from your profile');
  const email=$('email').value.trim().toLowerCase();
  if(email!==record.email)return notify('Enter the registered email first');
  if(!window.PublicKeyCredential || !navigator.credentials)
   return notify('Fingerprint is not supported in this browser');
  const result=await navigator.credentials.get({publicKey:{
   challenge:randomChallenge(),
   rpId:location.hostname,
   allowCredentials:[{
    type:'public-key',
    id:fromB64url(record.id)
   }],
   userVerification:'required',
   timeout:60000
  }});
  if(!result)return notify('Fingerprint verification failed');
  if(!users[record.email])return notify('Account not found');
  current=record.email;
  openApp();
  notify('Fingerprint login successful');
 }catch(e){
  notify('Fingerprint login failed: '+(e.message||'Try again'));
 }
};
'''

if marker not in s:
    raise SystemExit("AN GAGARA: Ba a sami wurin saka fingerprint code ba.")

s=s.replace(marker, fingerprint+"\n"+marker, 1)

p.write_text(s)
print("\nAN GAMA! DAN AREWA DATA SECURITY UPGRADE.")
