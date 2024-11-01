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
vec3(1.0, 0.033105, 0.0),
vec3(0.447988, 0.170645, 0.0),
vec3(0.0, 0.132868, 0.0),
vec3(0.0, 0.447988, 0.0)
};

const vec3 scratch_color = vec3(0.45);

void fragment() {
	int color_index = int(floor(UV2.x));
	vec3 color = colors[color_index];
	
	int metal_index = int(floor(UV2.y));
	vec3 metal_rough = metals[metal_index];
	
	METALLIC = metal_rough.r;
	ROUGHNESS = metal_rough.g;
	
	float edge = COLOR.g;
	float edge_scratch_mask = texture(scratches, UV2 * 8.0).r * edge;
	
	ALBEDO = mix(color, scratch_color, edge_scratch_mask);
	
	AO = COLOR.r;
	NORMAL_MAP = texture(trim_sheet, UV).rgb;
}