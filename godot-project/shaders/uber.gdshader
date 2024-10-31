shader_type spatial;

uniform sampler2D trim_sheet;
uniform sampler2D scratches;

const vec3 colors[] = {
	vec3(1.0, 0.160127, 0.055545),
	vec3(0.3568, 0.12862, 1.0),
	vec3(0.011984, 0.006903, 0.034534),
	vec3(0.671139, 0.717103, 1.0)
};

const vec3 metals[] = {
	vec3(1.0, 0.2, 0.0),
	vec3(0.7, 0.45, 0.0),
	vec3(0.0, 0.4, 0.0),
	vec3(0.0, 0.7, 0.0)
};

const vec3 scratch_color = vec3(0.45);

void fragment() {
	// color packed in RED
	float c = COLOR.r;
	
	// metal-roughness packed in GREEN
	float mr = COLOR.g;
	
	vec3 color = colors[0];
	if (c > 0.15 && c < 0.25) color = colors[1];
	else if (c > 0.25 && c < 0.35) color = colors[2];
	else if (c > 0.35 && c < 0.45) color = colors[3];
	
	vec3 metal_rough = metals[0];
	if (mr > 0.15 && mr < 0.25) metal_rough = metals[1];
	else if (mr > 0.25 && mr < 0.35) metal_rough = metals[2];
	else if (mr > 0.35 && mr < 0.45) metal_rough = metals[3];
	
	METALLIC = metal_rough.r;
	ROUGHNESS = metal_rough.g;
	
	// edge mask packed in ALPHA
	float edge = COLOR.a;
	float edge_scratch_mask = texture(scratches, UV2 * 8.0).r * edge;
	
	ALBEDO = mix(color, scratch_color, edge_scratch_mask);
	
	AO = COLOR.b;
	NORMAL_MAP = texture(trim_sheet, UV).rgb;
}