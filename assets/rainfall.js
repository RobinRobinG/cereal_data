function rain_collection(arr){
	var n = arr.length;
	var water = 0;
	var left_max = 0;
	var right_max = 0;
 	var lo_idx = 0;
 	var hi_idx = n - 1; 

 	while (lo_idx <= hi_idx){
 		if (arr[lo_idx] < arr[hi_idx]){
	 		if (arr[lo_idx] > left_max){
	 			left_max = arr[lo_idx];
	 		}
	 		else{
	 			water += left_max - arr[lo_idx];
	 		}
	 		lo_idx++;
 		}
 		else {
 			if (arr[hi_idx] > right_max){
 				right_max = arr[hi_idx];
 			}
 			else {
 				water += right_max - arr[hi_idx];
 			}
 			hi_idx--;
 		}
 	}
 	return water;
}
var arr = [7,0,0,0,0];
var x = rain_collection(arr);
console.log(x);


function binary_search (arr, val) {
//assume the arr is sorted.
	var arr_half = Math.floor(arr.length-1)/2;

	if (arr.length == 1 && arr[arr.length - 1] != val){
		return False;
	}
	else if (arr[arr_half] == val){
	//return the index of the val
		return arr_half;
	}
	else if (arr[arr_half] > val){
		return binary_search(arr.slice(0, arr_half), val);
	}
	else {
		return binary_search(arr.slice(arr_half), val);
	}
}


