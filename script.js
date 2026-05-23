// Helper to show SweetAlert2 messages
function showToast(icon, title) {
    Swal.fire({
        toast: true,
        position: 'top-end',
        icon: icon,
        title: title,
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });
}

// ========== NEW: Convert seconds to human readable format (mirrors Python convert) ==========
function convertSeconds(seconds) {
    if (!seconds || seconds <= 0) return "0 seconds";
    let days = Math.floor(seconds / 86400);
    seconds %= 86400;
    let hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    let minutes = Math.floor(seconds / 60);
    let secs = seconds % 60;
    
    let parts = [];
    if (days > 0) parts.push(`${days} Day${days !== 1 ? 's' : ''}`);
    if (hours > 0) parts.push(`${hours} Hour${hours !== 1 ? 's' : ''}`);
    if (minutes > 0) parts.push(`${minutes} Min${minutes !== 1 ? 's' : ''}`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs} Sec${secs !== 1 ? 's' : ''}`);
    return parts.join(' ');
}

// ========== UPDATED: Check Recovery Email with human readable output ==========
function checkRecovery() {
    const token = document.getElementById('checkToken').value;
    if (!token) {
        showToast('error', 'Access Token required');
        return;
    }
    
    axios.get('/api/get-bind-info', { params: { access_token: token } })
        .then(res => {
            const data = res.data;
            let output = '';
            
            // Build human-readable summary exactly like the standalone script
            const email = data.email || "";
            const emailToBe = data.email_to_be || "";
            const countdown = data.request_exec_countdown || 0;
            
            if (email === "" && emailToBe !== "") {
                output = `✅ Summary: Pending email confirmation: ${emailToBe} - Confirms in: ${convertSeconds(countdown)}\n`;
                output += `📧 Current email: None\n`;
                output += `⏳ Pending email : ${emailToBe}\n`;
                output += `⏰ Countdown    : ${convertSeconds(countdown)}`;
            } 
            else if (email !== "" && emailToBe === "") {
                output = `✅ Summary: Email confirmed: ${email}\n`;
                output += `📧 Current email: ${email}\n`;
                output += `🔒 Status       : Verified & Active`;
            }
            else if (email === "" && emailToBe === "") {
                output = `⚠️ Summary: No recovery email set\n`;
                output += `📧 Current email: None\n`;
                output += `⏳ Pending email : None`;
            }
            else {
                output = `ℹ️ Summary: Current: ${email} | Pending change: ${emailToBe}\n`;
                output += `📧 Current email: ${email}\n`;
                output += `⏳ Pending email : ${emailToBe}\n`;
                output += `⏰ Countdown    : ${convertSeconds(countdown)}`;
            }
            
            document.getElementById('checkResult').innerHTML = output.replace(/\n/g, '<br>');
            showToast('success', 'Information retrieved');
        })
        .catch(err => {
            console.error(err);
            document.getElementById('checkResult').innerHTML = '❌ Failed to fetch bind information.';
            showToast('error', 'Request failed');
        });
}

// ---------- All other functions (unchanged from previous version) ----------
// (sendOTP, bindEmail, resetAdd, checkPlatforms, cancelRequest, 
//  verifyUnbind, sendVerifyRequest, startChange, verifyOldIdentity, 
//  verifyNewOtp, revokeToken - keep exactly as provided earlier)

// ========== PASTE THE REST OF YOUR EXISTING FUNCTIONS HERE ==========
// (The functions below are unchanged – only checkRecovery and convertSeconds are new)

function sendOTP() {
    const email = document.getElementById('addEmail').value;
    const token = document.getElementById('addToken').value;
    if (!email || !token) {
        showToast('error', 'Email and Access Token required');
        return;
    }
    addState.email = email;
    addState.token = token;
    axios.post('/api/send-otp', { email, access_token: token })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', 'OTP sent!');
                document.getElementById('sendOtpBtn').style.display = 'none';
                document.getElementById('otpSection').style.display = 'block';
                addState.step = 'otp';
            } else {
                showToast('error', 'Failed to send OTP');
            }
        })
        .catch(() => showToast('error', 'Network error'));
}

let addState = { email: '', token: '', step: 'email' };

function bindEmail() {
    const otp = document.getElementById('otpCode').value;
    if (!otp) {
        showToast('error', 'Enter OTP');
        return;
    }
    axios.post('/api/verify-otp', { email: addState.email, access_token: addState.token, otp })
        .then(res => {
            if (res.data.result === 0 && res.data.verifier_token) {
                const verifier = res.data.verifier_token;
                return axios.post('/api/bind-email', { email: addState.email, access_token: addState.token, verifier_token: verifier });
            } else {
                throw new Error('OTP verification failed');
            }
        })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', `Email ${addState.email} bound successfully!`);
                resetAdd();
            } else {
                showToast('error', 'Bind failed');
            }
        })
        .catch(err => showToast('error', err.message || 'Bind error'));
}

function resetAdd() {
    document.getElementById('addEmail').value = '';
    document.getElementById('addToken').value = '';
    document.getElementById('otpCode').value = '';
    document.getElementById('sendOtpBtn').style.display = 'block';
    document.getElementById('otpSection').style.display = 'none';
    addState = { email: '', token: '', step: 'email' };
}

function checkPlatforms() {
    const token = document.getElementById('platformsToken').value;
    if (!token) { showToast('error', 'Access Token required'); return; }
    axios.get('/api/get-platforms', { params: { access_token: token } })
        .then(res => {
            const platforms = {3:'Facebook',8:'Gmail',10:'iCloud',5:'VK',11:'Twitter',7:'Huawei'};
            let output = '';
            if (res.data.bounded_accounts?.length) {
                res.data.bounded_accounts.forEach(acc => {
                    output += `${platforms[acc.platform] || 'Platform'+acc.platform}\n`;
                    if (acc.user_info?.email) output += `  📧 ${acc.user_info.email}\n`;
                    if (acc.user_info?.nickname) output += `  📝 ${acc.user_info.nickname}\n`;
                });
            } else {
                output = 'No secondary links found';
            }
            document.getElementById('platformsResult').innerText = output;
            showToast('success', 'Platforms loaded');
        })
        .catch(() => showToast('error', 'Failed'));
}

function cancelRequest() {
    const token = document.getElementById('cancelToken').value;
    if (!token) { showToast('error', 'Access Token required'); return; }
    axios.post('/api/cancel-request', { access_token: token })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', 'Recovery request cancelled');
                document.getElementById('cancelToken').value = '';
            } else {
                showToast('error', 'No active request');
            }
        })
        .catch(() => showToast('error', 'Failed'));
}

let unbindIdentity = null;

function verifyUnbind() {
    const email = document.getElementById('unbindEmail').value;
    const token = document.getElementById('unbindToken').value;
    const method = document.getElementById('unbindMethod').value;
    if (!email || !token) { showToast('error', 'Email and Token required'); return; }
    let payload = { email, access_token: token };
    if (method === 'otp') {
        Swal.fire({
            title: 'Enter OTP',
            input: 'text',
            inputPlaceholder: '6-digit OTP',
            showCancelButton: true
        }).then(result => {
            if (result.isConfirmed && result.value) {
                payload.otp = result.value;
                sendVerifyRequest(payload, token);
            }
        });
    } else {
        Swal.fire({
            title: 'Secondary Password',
            input: 'password',
            inputPlaceholder: 'Your secondary password',
            showCancelButton: true
        }).then(result => {
            if (result.isConfirmed && result.value) {
                payload.secondary_password = result.value;
                sendVerifyRequest(payload, token);
            }
        });
    }
}

function sendVerifyRequest(payload, token) {
    axios.post('/api/verify-identity', payload)
        .then(res => {
            if (res.data.result === 0 && res.data.identity_token) {
                unbindIdentity = res.data.identity_token;
                return axios.post('/api/create-unbind', { access_token: token, identity_token: unbindIdentity });
            } else {
                throw new Error('Identity verification failed');
            }
        })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', 'Email unbind request created');
                document.getElementById('unbindEmail').value = '';
                document.getElementById('unbindToken').value = '';
                unbindIdentity = null;
            } else {
                showToast('error', 'Unbind failed');
            }
        })
        .catch(err => showToast('error', err.message));
}

let changeState = { step: 'old', identityToken: null, verifierToken: null, oldEmail: '', newEmail: '', token: '' };

function startChange() {
    const oldEmail = document.getElementById('oldEmail').value;
    const newEmail = document.getElementById('newEmail').value;
    const token = document.getElementById('changeToken').value;
    const method = document.getElementById('changeMethod').value;
    if (!oldEmail || !newEmail || !token) {
        showToast('error', 'All fields required');
        return;
    }
    changeState.oldEmail = oldEmail;
    changeState.newEmail = newEmail;
    changeState.token = token;
    let payload = { email: oldEmail, access_token: token };
    if (method === 'otp') {
        Swal.fire({ title: 'OTP for old email', input: 'text' }).then(res => {
            if (res.isConfirmed && res.value) {
                payload.otp = res.value;
                verifyOldIdentity(payload);
            }
        });
    } else {
        Swal.fire({ title: 'Secondary Password', input: 'password' }).then(res => {
            if (res.isConfirmed && res.value) {
                payload.secondary_password = res.value;
                verifyOldIdentity(payload);
            }
        });
    }
}

function verifyOldIdentity(payload) {
    axios.post('/api/verify-identity', payload)
        .then(res => {
            if (res.data.result === 0 && res.data.identity_token) {
                changeState.identityToken = res.data.identity_token;
                return axios.post('/api/send-otp', { email: changeState.newEmail, access_token: changeState.token });
            } else {
                throw new Error('Old email verification failed');
            }
        })
        .then(res => {
            if (res.data.result === 0) {
                Swal.fire({ title: 'OTP sent to new email', input: 'text', inputPlaceholder: 'Enter OTP' }).then(res2 => {
                    if (res2.isConfirmed && res2.value) {
                        verifyNewOtp(res2.value);
                    }
                });
            } else {
                throw new Error('Failed to send OTP to new email');
            }
        })
        .catch(err => showToast('error', err.message));
}

function verifyNewOtp(otp) {
    axios.post('/api/verify-otp', { email: changeState.newEmail, access_token: changeState.token, otp })
        .then(res => {
            if (res.data.result === 0 && res.data.verifier_token) {
                changeState.verifierToken = res.data.verifier_token;
                return axios.post('/api/rebind', {
                    identity_token: changeState.identityToken,
                    email: changeState.newEmail,
                    access_token: changeState.token,
                    verifier_token: changeState.verifierToken
                });
            } else {
                throw new Error('New email OTP invalid');
            }
        })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', 'Email changed successfully!');
                document.getElementById('oldEmail').value = '';
                document.getElementById('newEmail').value = '';
                document.getElementById('changeToken').value = '';
                changeState = { step: 'old', identityToken: null, verifierToken: null };
            } else {
                showToast('error', 'Rebind failed');
            }
        })
        .catch(err => showToast('error', err.message));
}

function revokeToken() {
    const token = document.getElementById('revokeToken').value;
    if (!token) { showToast('error', 'Access Token required'); return; }
    axios.post('/api/revoke-token', { access_token: token })
        .then(res => {
            if (res.data.result === 0) {
                showToast('success', 'Token revoked');
                document.getElementById('revokeToken').value = '';
            } else {
                showToast('error', 'Revoke failed');
            }
        })
        .catch(() => showToast('error', 'Revoke error'));
}