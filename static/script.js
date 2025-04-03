
document.querySelector('form').addEventListener('submit', function(event) {
  const age = document.getElementById('age').value;
  const gender = document.getElementById('gender').value;
  const chest_pain = document.getElementById('chest_pain').value;
  const restingbp = document.getElementById('restingbp').value;
  const serum_cholesterol = document.getElementById('serum_cholesterol').value;
  const fasting_blood_sugar = document.querySelector('input[name="fasting_blood_sugar"]:checked');
  const resting_ecg = document.getElementById('resting_ecg').value;
  const max_hr = document.getElementById('max_hr').value;
  const exercise_angina = document.querySelector('input[name="exercise_angina"]:checked');
  const oldpeak = document.getElementById('oldpeak').value;
  const slope = document.getElementById('slope').value;
  const ca = document.getElementById('ca').value;
  const thal = document.getElementById('thal').value;


  if (!age || !gender || !chest_pain || !restingbp || !serum_cholesterol || !fasting_blood_sugar || 
      !resting_ecg || !max_hr || !exercise_angina || !oldpeak || !slope || !ca || !thal) {
      alert("Please fill in all fields.");
      event.preventDefault();
  }
});
